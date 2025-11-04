#!/usr/bin/env bash
#
# geo_cn_whitelist.sh
# -------------------------------------------------
# 1. 下载 GeoLite2-Country-CSV.zip
# 2. 解压到 /tmp/GeoLite2-Country-CSV
# 3. 过滤出 China 的 IPv4 网段
# 4. 输出 white-list-cn.conf
# 5. 清理临时目录
# -------------------------------------------------

set -euo pipefail

# 如需账号 / 许可证，请把下面两行改成自己的
MAXMIND_LICENSE="${MAXMIND_LICENSE:-}"
MAXMIND_ACCOUNT_ID="${MAXMIND_ACCOUNT_ID:-}"
TMP_ZIP_PATH="/tmp/GeoLite2-Country-CSV.zip"
TMP_DIR="/tmp/GeoLite2-Country-CSV"
OUTPUT_FILE="${OUTPUT_WHITE_LIST_PATH}"

echo ">>> 检测环境变量 ..."
echo "MAXMIND_LICENSE : ${MAXMIND_LICENSE}"
echo "MAXMIND_ACCOUNT_ID : ${MAXMIND_ACCOUNT_ID}"


if [[ -z "$MAXMIND_LICENSE" ]]; then
    echo "请设置环境变量 MAXMIND_LICENSE=<你的 MAXMIND_LICENSE>"
    exit 1
fi
if [[ -z "$MAXMIND_ACCOUNT_ID" ]]; then
    echo "请设置环境变量 MAXMIND_ACCOUNT_ID=<你的 MAXMIND_ACCOUNT_ID>"
    exit 1
fi


# 1. 下载
echo ">>> 正在下载 GeoLite2-Country-CSV.zip ..."
curl -L -u "${MAXMIND_ACCOUNT_ID}:${MAXMIND_LICENSE}" \
     "https://download.maxmind.com/geoip/databases/GeoLite2-Country-CSV/download?suffix=zip" \
     > "${TMP_ZIP_PATH}"

# 2. 解压
echo ">>> 解压到 ${TMP_DIR} ..."
rm -rf "${TMP_DIR}"
unzip -q "${TMP_ZIP_PATH}" -d /tmp
# 解压后目录名里带日期，例如 GeoLite2-Country-CSV_20240807
CSV_DIR=$(find /tmp -maxdepth 1 -type d -name 'GeoLite2-Country-CSV_*')
mv "${CSV_DIR}" "${TMP_DIR}"

# === 开始计时 ===
start_ts=$(date +%s.%N)

# 3. 找到 China 的 geoname_id
CHINA_ID=$(awk -F, '$5=="CN" {print $1}' "${TMP_DIR}/GeoLite2-Country-Locations-en.csv")

# 4. 过滤出 China 的 IPv4 CIDR，并写成 Nginx allow 格式
echo ">>> 生成 ${OUTPUT_FILE} ..."
mkdir -p "$(dirname "${OUTPUT_FILE}")"  
awk -F, -v id="${CHINA_ID}" '$2==id {print "allow " $1 ";"}' \
    "${TMP_DIR}/GeoLite2-Country-Blocks-IPv4.csv" > "${OUTPUT_FILE}"

# === 结束计时并输出 ===
end_ts=$(date +%s.%N)
elapsed=$(awk -v s="$start_ts" -v e="$end_ts" 'BEGIN{printf "%.6f", e - s}')
echo ">>> 字符串处理完成 耗时 : ${elapsed} 秒 \n"
echo ">>> 完成！共写入 $(wc -l < "${OUTPUT_FILE}") 条记录到 ${OUTPUT_FILE}"

# 5. 清理
echo ">>> 清理临时文件 ..."
rm -rf "${TMP_ZIP_PATH}" "${TMP_DIR}"

