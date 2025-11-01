class ErrorMessage:
    """自定义异常信息"""

    args_not_found = '''未在命令行参数中找到"{short_arg}" 或 "{long_arg}"'''

    parse_config_failed = """读取配置相关内容时发生错误 , 错误信息 : {exc}"""

    version_code_invalid = '''处理版本号时发生异常 , 版本号格式不合法 , 原因 : {exc}"'''

    picker_not_found = """未找到"{picker_type}"类型的提取器 , 请检查是否配置了"{picker_type}"类型的提取器"""

    too_mach_pick_types = """不能在不使用正则匹配的情况下填写超过1个"pick_types" , 错误的"pick_types"位于 : {picker_type}"""

    pick_types_is_empty = """"pick_types"不能为空 , 错误的"pick_types"位于 : {picker}"""

    error_in_search_lines = """处理归档内容第 {line_index} 行时发生错误 , 此行内容将被跳过判断 , 行内容为 : {line} , 错误信息 : {exc}"""

    column_index_out_of_range = """应用picker时"column_index"超出了范围 , 此行只分割出了{column_number}个元素而"column_index"为{column_index} , 请检查此行格式以及picker配置是否正确 , 错误的"column_index"位于 : {picker}"""

    incorrect_line_format = (
        """行分隔符 "{table_separator}" 无法对此行有效分隔 , 请检查此行格式是否正确"""
    )

    reformat_line_error = """重新格式化归档内容时发生错误 , 此行内容将被跳过处理 , 原内容为 : {line} , 错误信息 : {exc}"""

    collect_document_error = """拉取第{index}个归档文件源时发生错误 , 跳过此归档文件源的拉取 , 错误信息 : {exc}"""

    write_file_error = """写入归档文件时发生错误 , 错误信息 : {exc}"""


class ParseConfigError(Exception):
    """解析配置文件时发生错误"""


class PickerNotFoundError(Exception):
    """未找到指定类型的选择器"""


class SearchLineError(Exception):
    """根据版本号范围匹配内容时发生错误"""


class ReformatLineError(Exception):
    """重新格式化归档内容时发生错误"""
