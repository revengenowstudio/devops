import os


def main():
    # 从各种地方读取配置，例如配置文件，环境变量等。
    # 起码包含归档文件的raw_url，最小版本号，最大版本号等等

    # get下来归档文件之后，把内容读到一个专门的归档文件处理类里，
    # 后面的处理通过这个类的函数组合进行

    # 分别将文本内容读进归档文件处理类后，将这些对象放进一个列表里
    # 。后面直接for这个列表分别调用这些对象的函数

    # 在类中查找并匹配出符合版本号区间的行，
    # 并最后直接以文本追加模式输出到输出文件里
    
    # https://docs.github.com/zh/rest/repos/contents?apiVersion=2022-11-28
    # GET /repos/{owner}/{repo}/contents/{path}
    

    pass

    

if __name__ == '__main__':
    main()    
    
