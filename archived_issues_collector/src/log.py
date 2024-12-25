class Log():
    '''日志信息'''
    archived_source = '''第{index}个归档文件源'''
    archived_content = '''归档文件内容'''
    version_start = '''起始版本号'''
    version_end = '''结束版本号'''
    

    getting_something = '''获取 {something} 中'''
    getting_something_from = '''正在从 {another} 中获取 {something}'''
    loading_something = '''加载 {something} 中'''
    config_path_not_found = '''未在命令行参数中获取到配置文件路径 , 请正确使用"-c"或"--config"参数传入配置文件路径'''
    load_archived_source = '''读取到{count}条归档文件源的配置内容'''
    match_archive_content_in_version_range = '''正在匹配符合版本范围的归档内容'''
    match_much_archive_content = '''匹配到{count}条符合版本范围的归档内容'''
    write_content_to = '''正在将匹配到的内容写入到 {path}'''
    input_version_range = '''输入的版本号范围为："{start}" - "{end}"'''
    match_introduce_version = '''是否匹配引入版本号：{match_introduce_version}'''
    input_version_empty = '''输入的版本号为空'''
    http_404_not_found = '''无法请求到对应url , 请检查输入的url是否正确 , 请求失败的url为 : {url}'''
    http_401_unauthorized = '''没有权限请求对应url , 请检查token是否正确配置以及token拥有正确的权限 , 请求失败的url为 : {url}'''
    http_status_error = '''HTTP请求返回状态码错误 , 原因：{reason}'''
    collect_document_success_number = '''总共成功获取到了{number}份归档文件'''
    
    job_done = '''脚本执行完毕'''

    loading_something_success = '''加载 {something} 完毕'''
    getting_something_from_success = '''成功从 {another} 中获取 {something}'''
    write_content_success = '''成功将匹配到的内容写入到 {path}'''
