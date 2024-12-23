import sys

from log import Log
from exception import ErrorMessage


def get_value_from_args(short_arg: str,
                        long_arg: str) -> str:
    argv = sys.argv
    result = None
    if (long_arg in argv):
        result = argv[argv.index(long_arg) + 1]
    if (short_arg in argv != -1):
        result = argv[argv.index(short_arg) + 1]

    if result is None:
        raise ValueError(
            ErrorMessage.args_not_found
            .format(short_arg=short_arg,
                    long_arg=long_arg
                    )
        )
    return result


def get_value_from_args_or_default(short_arg: str,
                                   long_arg: str) -> str:
    '''如果找不到对应的命令行参数，返回空字符串'''
    result = ""
    try:
        get_value_from_args(short_arg, long_arg)
    except ValueError:
        pass
    return result
