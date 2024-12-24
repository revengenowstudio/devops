class ErrorMessage():
    '''自定义异常信息'''

    args_not_found = '''未在命令行参数中找到"{short_arg}" 或 "{long_arg}"'''

    parse_config_failed = '''读取配置相关内容时发生错误，错误信息 ： {exc}'''

    version_code_invalid = '''处理版本号时发生异常，版本号格式不合法，原因： {exc}"'''

    picker_not_found = '''未找到"{picker_type}"类型的提取器'''

    too_mach_pick_types = '''不能在不使用正则匹配的情况下填写超过1个"pick_types" , 错误的"pick_types"位于 : {picker_type}'''
    
    pick_types_is_empty = '''"pick_types"不能为空，错误的"pick_types"位于 : {picker}'''


class ParseConfigError(Exception):
    '''解析配置文件时发生错误'''


class PickerNotFoundError(Exception):
    '''未找到指定类型的选择器'''
