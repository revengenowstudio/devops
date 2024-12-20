import re
from enum import IntEnum
import string
from typing import Iterator


class VersionType(IntEnum):
    old = 1
    new = 2
    special = 0


class VersionCode():

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

        return VersionType.special

    def __init__(self, raw_version: str) -> None:
        self.__raw: str = raw_version
        self.__version_type = self.__check_version_type(raw_version)

        self.__split_version: list[str] = [raw_version]
        if self.__version_type != VersionType.special:
            self.__split_version = self.__split_version_to_list(raw_version)

    def to_int64(self) -> int:
        result: int = 0
        if self.type == VersionType.special:
            # 特殊版本号永远要比其他版本号小
            return result

        parts = self.__convert_parts_to_int(self.parts)

        # 版本号映射到int64的关系如下：
        # 0.99.914b55
        # 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000
        #           0         9    9         9    1    4    b         5    5    空着

        # G1028P3
        # 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000
        #                               G         1    0    2    8    P         3
        # 这里的bit_per_part表示版本号是怎么映射的，每部分占多少bit
        bit_per_part: list[int] = [8, 8, 16, 8, 8]
        if self.type == VersionType.old:
            bit_per_part = [8, 16, 8, 8]
            
        total_bit = sum(bit_per_part)
        # total_bit = 56

        # for index, part in enumerate(parts):
        #     if index == 0:
        #         result = part << (total_bit -
        #                           sum(bit_per_part[:index+1]))
        #         continue
        #     result |= part << (
        #         total_bit - sum(bit_per_part[:index+1]))
        
        # 从高位到低位依次组合各部分
        for index, part in enumerate(parts):
            # 计算当前部分的位移量
            shift_amount = total_bit - sum(bit_per_part[:index+1])
            # 使用按位或操作将当前部分组合到 result 中
            result |= (part & ((1 << bit_per_part[index]) - 1)) << shift_amount

        # result = (parts[0] << 40) | (parts[1] << 32) | (
        #     parts[2] << 16) | (parts[3] << 8) | parts[4]

        if self.type == VersionType.new:
            # 新版本号永远要比旧版本大
            result = result << 4
        
        print(f'{self.__raw} :'
            , self.parts)
        bin_text = re.findall(".{4}",bin(result)[2:])
        print(f'{self.__raw} :'
            ," ".join(bin_text))
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


# class Version(ABC):
#     def __init__(self, raw_version: str) -> None:
#         self.__raw: str
#         self.__split_version: list[int]

#     @abstractmethod
#     def __lt__(self, other_version: 'Version') -> bool:
#         '''self < other_version'''
#         pass

#     def __le__(self, other_version: 'Version') -> bool:
#         '''self > other_version'''
#         if self < other_version:
#             return False
#         else:
#             return True

#     def __eq__(self, other_version: 'Version') -> bool:
#         '''self == other_version'''
#         if str(self) == str(other_version):
#             return True
#         else:
#             return False

#     def __repr__(self) -> str:
#         return self.__raw

#     def __str__(self) -> str:
#         return self.__raw

#     def __getitem__(self, index: int | slice) -> int | list[int]:
#         return self.__split_version[index]

#     def __iter__(self) -> Iterator[int]:
#         return iter(self.__split_version)


# class NewVersion(Version):
#     '''处理类似"0.99.915"的新版本号的类，可直接比较大小'''

#     def __init__(self, raw_version: str) -> None:
#         super().__init__(raw_version)
#         self.__raw: str = raw_version
#         if "." not in raw_version:
#             raise ValueError(
#                 f"{raw_version} is not a valid new version string")

#         # TODO 这里还没考虑  "0.99.914b55" 后面有字母的情况
#         self.__split_version = list(map(int, raw_version.split(".")))

#     def __lt__(self, other_version: Version) -> bool:
#         if isinstance(other_version, OldVersion):
#             return False

#         other_version_more_item = False
#         for index, self_sub_version in enumerate(self.__split_version):
#             try:
#                 if self_sub_version < other_version.__split_version[index]:
#                     return True
#             except IndexError:
#                 other_version_more_item = True

#         if (other_version_more_item):
#             other_max_index = len(other_version.__split_version) - 1
#             if self[0:other_max_index] == other_version.__split_version:
#                 return True

#             for index, self_sub_version in enumerate(self.__split_version[other_max_index:]):
#                 if self_sub_version > other_version.__split_version[index]:
#                     return False

#         return False


# class OldVersion(Version):
#     '''处理类似"G1024"的新版本号的类，可直接比较大小'''

#     @staticmethod
#     def __split_per_two_char(raw_version: str) -> list[int]:
#         result: list[int] = []
#         for index, char in enumerate(range(1, len(raw_version))):
#             if index % 2 == 0:
#                 result.append(int(raw_version[index:index+1]))
#         return result

#     def __init__(self, raw_version: str) -> None:
#         super().__init__(raw_version)
#         self.__raw: str = raw_version
#         if "." in raw_version:
#             raise ValueError(
#                 f"{raw_version} is a new version string")
#         if not raw_version[0].isalpha():
#             raise ValueError(
#                 f"{raw_version} is not a valid old version string")
#         self.__split_version = [
#             ord(raw_version[0]), *self.__split_per_two_char(raw_version)
#         ]

#     def __lt__(self, other_version: Version) -> bool:
#         if isinstance(other_version, NewVersion):
#             return True

#         for index, self_sub_version in enumerate(self.__split_version):
#             if self_sub_version < other_version.__split_version[index]:
#                 return True
#         return False
