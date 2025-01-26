

## 配置文件变量

- 配置文件位于 [config.json](config.json)

| 变量名                                           | 类型                | 默认值 | 描述                                                                                                                                                                                                                            |
| ------------------------------------------------ | ------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| archived_issues_info                             | list[dict[str,Any]] | []     | 定义归档文件源获取规则,目前只支持http和https源,配置时请参考[归档文件url配置说明](#归档文件url配置说明)                                                                                                                          |
| archived_issues_info[].url                       | str                 | ""     | 归档文件源的url                                                                                                                                                                                                                 |
| archived_issues_info[].json_api                  | bool                | false  | 请求的url是否是json api,若此值为true,请求url后响应的内容将以json格式解析                                                                                                                                                        |
| archived_issues_info[].content_key               | str                 | ""     | 实际归档内容在json响应中的键名,`json_api`值为true时才生效,与`json_api`配合使用                                                                                                                                                  |
| archived_issues_info[].base64_decode             | bool                | false  | 请求url后响应的内容是否需要base64解码                                                                                                                                                                                           |
| archived_issues_info[].use_token                 | bool                | false  | 请求url时是否在请求头中携带token                                                                                                                                                                                                |
| archived_issues_info[].http_headers              | dict[str,str]       | {}     | 请求url时要携带的请求头内容                                                                                                                                                                                                     |
| archive_document.skip_header_rows                | int                 | 0      | 处理每个原始归档文档内容时,从第一行开始要跳过多少行,因为开头的几行可能是列表的开头格式,不能参与内容的处理                                                                                                                       |
| archive_document.table_separator                 | str                 | ""     | 表分隔符,用于分割原始归档文档内容中的每一行                                                                                                                                                                                     |
| archive_document.reformat_template               | str                 | ""     | 用于重新格式化归档内容的格式模版,可使用特殊占位符变量来灵活定制输出格式,可用的变量有: `{issue_type}` `{issue_location}`  `{issue_url_parents}` `{issue_title}` `{md_link_square_start}` `{md_link_square_end}` `{first_number}` |
| archive_document.raw_line_pickers                | list[dict[str,Any]] | []     | picker用来分类和提取`table_separator`分隔好的内容,可定义多个picker,请确保`column_index`不会超出`table_separator`分割后的column个数                                                                                              |
| archive_document.raw_line_pickers[].column_index | int                 | 0      | picker的列索引,每个column就是每行内容通过`table_separator`拆分出来的每个元素,`column_index`表示了这个picker `pick_types` `regex` 的要被应用在第几个column                                                                       |
| archive_document.raw_line_pickers[].pick_types   | list[str]           | []     | picker要匹配内容的内容类型,名称与大部分`reformat_template`的占位符变量是对应的,由于正则可以设置多个捕获组,所以根据正则匹配后的匹配结果顺序一一对应此列表中的类型;在`regex`为null时,此列表只能填写一个元素                       |
| archive_document.raw_line_pickers[].regex        | str                 | None   | picker匹配内容的正则表达式,值为null时则不使用正则而是使用整个column的字符串,可使用捕获组将正则匹配内容与`pick_types`中的类型进行对应,若捕获组个数大于`pick_types`中元素的个数,多余的捕获组结果则会被丢弃                        |
| output_path                                      | str                 | ""     | 输出格式化后内容的文件路径                                                                                                                                                                                                      |

## 流水线所需仓库机密或变量
- 仓库机密
  - `REPOSITORY_TOKEN` : 需要所有目标仓库的`Content`的`读取`权限

## 归档文件url配置说明

### github
- 目前发现可以有两种填写方式可以满足拉取归档文件的需求
  - 通过 Restful API 来获取内容
    - 详见 [存储库内容的 REST API 终结点 - Get repository content](https://docs.github.com/zh/rest/repos/contents?apiVersion=2022-11-28#get-repository-content)
    - url 样例 : `https://api.github.com/repos/<owner>/<repo>/contents/<path>` 
    - 可以通过控制Http Header中的`Accept`的值来控制返回内容的格式
      - `application/vnd.github.raw+json` 则返回整个文件原内容,此种方式支持文件内容大小为**1MB**至**100MB**的文件
      - `application/vnd.github.object+json` 则返回json对象 , json对象也包含了经过base64编码的文件内容,位于`content`字段中,此种方式只支持文件内容大小为**1MB**的文件

  - 通过 raw.githubusercontent.com 获取内容
    - url 样例 : `https://raw.githubusercontent.com/<owner>/<repo>/refs/heads/<branch>/<path>` 
    - 此方式支持任意大小的文件,但是在本地运行时没有特殊手段则无法访问
    - 当仓库为`private`状态,使用时需要在添加query params(请求参数)`token`,这里的token是由github网页临时生成的,有效期很短且不支持用户的access token来鉴权

### gitlab/bitbucket
  - 通过`git fetch`拉取git仓库 获取内容
    - 由于bitbucket没有永久url可以指向git分支中某个文件的最新版本,所以需要另辟蹊径,使用`git fetch`的方式拉取整个仓库(或部分文件)的最新内容
    - 具体实现方式详见[git_fetch.sh](../script/git_fetch.sh)
    - 其中[git_fetch.sh]的 "$REMOTE_GIT_URL" 是这个格式的 : `https://x-token-auth:<personal_token>@bitbucket.org/<username>/<repo>.git`,需要根据这个格式填入正确的内容,并将这个url以Github Secret 的形式让脚本能够使用这个url
    - 拉取文档的工作已经交给[git_fetch.sh],那么[config.json](config.json)配置里的url,样例为 : `file://fetch_file/<path>`
