import re
import string
from enum import IntEnum
from typing import Iterator

from exception import ErrorMessage
from log import Log


class VersionType(IntEnum):
    infinite = -1
    infinitesimal = 0
    old = 1
    new = 2


class VersionCode():

    @staticmethod
    def should_version_valid(raw_version: str) -> None:
        if raw_version == "":
            raise ValueError(
                Log.input_version_empty)

    @staticmethod
    def __split_version_to_list(raw_version: str) -> list[str]:
        # 使用正则表达式匹配数字和单个字母
        parts: list[str] = re.findall(r'\d+|[a-zA-Z]', raw_version)
        return parts

    @staticmethod
    def __convert_parts_to_int(parts: list[str]) -> list[int]:
        converted = []
        for part in parts:
            if part.isdigit():
                # 数字部分直接转换为整数
                converted.append(int(part))
            else:
                # 字母部分转换为 ASCII 码值，假设是小写字母
                # converted.append(ord(part.lower()) - ord('a') + 1)
                converted.append(ord(part.lower()))
        return converted

    @property
    def type(self) -> VersionType:
        return self.__version_type

    @property
    def parts(self) -> list[str]:
        return self.__split_version

    @staticmethod
    def __check_version_type(raw_version: str) -> VersionType:
        if "." in raw_version:
            return VersionType.new
        if raw_version[0] in string.ascii_letters:
            return VersionType.old

        return VersionType.infinitesimal

    def __init__(self,
                 raw_version: str = "",
                 infinitesimal_version: bool = False,
                 infinite_version: bool = False
                 ) -> None:
        self.__raw: str = raw_version
        if (infinitesimal_version
                or raw_version == ""):
            self.__version_type = VersionType.infinitesimal
        elif infinite_version:
            self.__version_type = VersionType.infinite
            raw_version = "∞"
        else:
            self.__version_type = self.__check_version_type(raw_version)

        self.__split_version: list[str] = [raw_version]
        if self.__version_type not in (VersionType.infinitesimal,
                                       VersionType.infinite):
            self.__split_version = self.__split_version_to_list(raw_version)

    def to_int64(self) -> int:
        result: int = 0
        if self.type == VersionType.infinitesimal:
            # 特殊版本号永远要比其他版本号小
            return result

        bit_per_part: list[int] = [8, 8, 16, 8, 8]
        if self.type == VersionType.old:
            bit_per_part = [8, 16, 8, 8]
            
        if self.type == VersionType.infinite:
            # 无穷打版本号永远要比其他版本号大
            return (1 << (sum(bit_per_part) +1)) -1 

        parts = self.__convert_parts_to_int(self.parts)

        # 版本号映射到int64的关系如下：
        # 0.99.914b55 , [0,99,914,98,55]
        # 0000_0000_0000_0000_0110_0011_0000_0011_1001_0010_0110_0010_0011_0111_0000_0000
        #               0             99                 914         b        55    左移4位

        # 0000_0000_0000_0000_0110_0011_0000_0011_1001_0100_0000_0000_0000_0000_0000_0000
        #               0             99                 916                        左移4位
        #    0.99.916 :    0b_0110_0011_0000_0011_1001_0100_0000_0000_0000_0000
        # 子版本号位置置1 :  0b_0110_0011_0000_0011_1001_0100_1111_1111_1111_1111_0000

        # G1028P3 , [103,1028,112,3]
        # 0000 0000 0000 0000 0000 0000 0110 0111 0000 0000 0100 0100 0111 0000 0011 0000
        #                                       G                1028         P    3
        # 这里的bit_per_part表示版本号是怎么映射的，每部分占多少bit

        total_bit = sum(bit_per_part)

        # 从高位到低位依次组合各部分
        for index, part in enumerate(parts):
            # 计算当前部分的位移量
            shift_amount = total_bit - sum(bit_per_part[:index+1])
            # 使用按位或操作将当前部分组合到 result 中
            result |= (part & ((1 << bit_per_part[index]) - 1)) << shift_amount

        if self.type == VersionType.new:
            # 新版本号永远要比旧版本大
            result = result << 4
            if len(parts) == 3:
                # 正式版本号永远大于测试版本号 , 0.99.916 > 0.99.916b2
                # 所以正式版本号的子版本号二进制位全部置1
                mask = 0b1111_1111_1111_1111_0000
                result = result | mask

        # 测试用打印int64映射结果
        # print(f'{self.__raw} :'
        #     , self.parts)
        # bin_text = re.findall(".{4}",bin(result)[2:])
        # print(f'{self.__raw} :'
        #     ," ".join(bin_text))
        return result

    def __lt__(self, other_version: 'VersionCode') -> bool:
        '''self < other_version'''
        if self == other_version:
            return False
        if self.to_int64() < other_version.to_int64():
            return True
        else:
            return False

    def __le__(self, other_version: 'VersionCode') -> bool:
        '''self <= other_version'''
        if self == other_version:
            return True
        if self < other_version:
            return True
        else:
            return False

    def __gt__(self, other_version: 'VersionCode') -> bool:
        '''self > other_version'''
        if self == other_version:
            return False
        if self < other_version:
            return False
        else:
            return True

    def __ge__(self, other_version: 'VersionCode') -> bool:
        '''self >= other_version'''
        if self == other_version:
            return True
        if self < other_version:
            return False
        else:
            return True

    def __ne__(self, other_version: 'VersionCode') -> bool:
        '''self != other_version'''
        return not self.__eq__(other_version)

    def __eq__(self, other_version: 'VersionCode') -> bool:
        '''self == other_version'''
        if (str(self) == str(other_version)
                or self.to_int64() == other_version.to_int64()):
            return True
        else:
            return False

    def __repr__(self) -> str:
        return self.__raw

    def __str__(self) -> str:
        return self.__raw

    def __getitem__(self, index: int | slice) -> str | list[str]:
        return self.__split_version[index]

    def __iter__(self) -> Iterator[str]:
        return iter(self.__split_version)
