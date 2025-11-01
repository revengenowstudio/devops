class Log:
    """日志信息"""

    archived_source = """第{index}个归档文件源"""
    archived_content = """归档文件内容"""
    version_start = """起始版本号"""
    version_end = """结束版本号"""

    getting_something = """获取 {something} 中"""
    getting_something_from = """正在从 {another} 中获取 {something}"""
    loading_something = """加载 {something} 中"""
    config_path_not_found = """未在命令行参数中获取到配置文件路径 , 请正确使用"-c"或"--config"参数传入配置文件路径"""
    load_archived_source = """读取到{count}条归档文件源的配置内容"""
    match_archive_content_in_version_range = """正在匹配符合版本范围的归档内容"""
    match_much_archive_content = """匹配到{count}条符合版本范围的归档内容"""
    write_content_to = """正在将匹配到的内容写入到 {path}"""
    input_version_range = '''输入的版本号范围为："{start}" - "{end}"'''
    ignore_introduce_version = """忽略引入版本号：{ignore_introduce_version}"""
    include_start_version = """是否包含起始版本号：{result}"""
    include_end_version = """是否包含结束版本号：{result}"""
    input_version_empty = """输入的版本号为空"""
    http_404_not_found = (
        """无法请求到对应url , 请检查输入的url是否正确 , 请求失败的url为 : {url}"""
    )
    http_401_unauthorized = """没有权限请求对应url , 请检查token是否正确配置以及token拥有正确的权限 , 请求失败的url为 : {url}"""
    http_status_error = """HTTP请求返回状态码错误 , 原因：{reason}"""
    collect_document_success_number = """总共成功获取到了{number}份归档文件"""
    repository_token_not_found = """未在命令行参数以及环境变量中读取到Token"""

    job_done = """脚本执行完毕"""

    loading_something_success = """加载 {something} 完毕"""
    getting_something_from_success = """成功从 {another} 中获取 {something}"""
    write_content_success = """成功将匹配到的内容写入到 {path}"""

    help_message = """
    ---命令行参数帮助--- \n
    * -c --config 
    必填                   
    类型 : 字符串
    描述 : 配置文件路径

    * -vs --version-start 
    必填           
    类型 : 字符串
    描述 : 起始(最小)版本号,用于筛选出特定的归档内容

    * -ve --version-end 
    必填             
    类型 : 字符串
    描述 : 结束(最大)版本号,用于筛选出特定的归档内容

    -t --repository-token    
    选填        
    类型 : 字符串
    描述: A ccess token,若填写则请求归档文件时会携带此token

    -iiv --ignore-introduce-version   
    选填
    类型 : 字符串
    描述 : 筛选归档内容时忽略引入版本号,默认为否,使用时需要再后面添加true


    示例 :
    python main.py                       \\
    --config "./config/config.json"      \\
    --version-start "0.99.918"            \\
    --version-end "0.99.918"              \\
    --repository-token "test_token"       \\  
    --ignore-introduce-version true        \\
    """
