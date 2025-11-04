import ipaddress
import os
import json
from pathlib import Path


def load_and_parse_ip_white_list(
    path: Path,
) -> list[ipaddress.IPv4Network | ipaddress.IPv6Network]:
    result: list[ipaddress.IPv4Network | ipaddress.IPv6Network] = []
    print(f'读取ip白名单conf文件 : "{path}"')
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()
    # 每行格式是这样的 allow 1.0.32.0/19;
    for line in lines:
        result.append(
            ipaddress.ip_network(line.strip().replace("allow ", "").replace(";", ""))
        )

    return result


def is_ip_in_list(
    ip_str: str, networks: list[ipaddress.IPv4Network | ipaddress.IPv6Network]
) -> tuple[bool, ipaddress.IPv4Network | ipaddress.IPv6Network | None]:
    """判断一个 IP 字符串是否属于 ip_list 中的任一 CIDR 段"""
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        print(f"{ip_str} 不是有效的 IP 地址")
        return False, None

    for net in networks:
        if ip in net:
            return True, net

    return False, None


def mask_ip(ip_str: str):
    parts = ip_str.split(".")
    subnet = ""
    if "/" in parts[-1]:
        _, subnet = parts[-1].split("/")
        subnet = "/" + subnet
    return f"{parts[0]}.{parts[1]}.*.*{subnet}"


def verify_ip_in_networks(
    test_cn_ips: list[str],
    test_foreign_ips: list[str],
    networks: list[ipaddress.IPv4Network | ipaddress.IPv6Network],
):
    verify_ip_result: list[
        tuple[str, str, bool, ipaddress.IPv4Network | ipaddress.IPv6Network | None]
    ] = []
    verify_ip_result += [
        ("CN", cn_ip, *is_ip_in_list(cn_ip, networks)) for cn_ip in test_cn_ips
    ]
    verify_ip_result += [
        ("Other", foreign_ip, *is_ip_in_list(foreign_ip, networks))
        for foreign_ip in test_foreign_ips
    ]

    verify_ip_result.sort(
        key=lambda x: (x[0], x[2]),
    )
    print("测试特定IP地址是否匹配ip白名单中")
    for country_code, cn_ip, result, net in verify_ip_result:
        print(
            f"{country_code:<6} {mask_ip(cn_ip):<11} -> {f'命中{" ":<3}{mask_ip(str(net))}' if result else '未命中'}"
        )

    # 使用列表过滤器过滤 cn,false Other,true 的元组出来
    filtered = [
        (cc, ip, result, net)  # 原四元组
        for cc, ip, result, net in verify_ip_result
        if (cc == "CN" and result is False) or (cc == "Other" and result is True)
    ]
    if filtered:
        raise ValueError("发现目标CN IP不在白名单内或非CN IP在白名单内")


if __name__ == "__main__":
    test_cn_ips = os.environ.get("TEST_CN_IPS")
    test_foreign_ips = os.environ.get("TEST_FOREIGN_IPS")
    ip_white_list_path = os.environ.get("OUTPUT_WHITE_LIST_PATH")
    if not ip_white_list_path:
        raise KeyError('未设置环境变量 "OUTPUT_WHITE_LIST_PATH"')
    ip_white_list_path = Path(ip_white_list_path)

    if not test_cn_ips or not test_foreign_ips:
        raise KeyError('未设置环境变量 "TEST_CN_IPS" 或 "TEST_FOREIGN_IPS"')
    test_cn_ips = json.loads(test_cn_ips)
    test_foreign_ips = json.loads(test_foreign_ips)
    networks = load_and_parse_ip_white_list(ip_white_list_path)
    verify_ip_in_networks(test_cn_ips, test_foreign_ips, networks)
