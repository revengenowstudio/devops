class ErrorMessage():
    '''自定义异常信息'''

    args_not_found = '''未在命令行参数中找到"{short_arg}" 或 "{long_arg}"'''
    
    parse_config_failed = '''读取配置相关内容时发生错误，错误信息 ： {exc}'''

    version_code_invalid = '''处理版本号时发生异常，版本号格式不合法，原因： {exc}"'''
    
class ParseConfigError(Exception):
    '''解析配置文件时发生错误'''