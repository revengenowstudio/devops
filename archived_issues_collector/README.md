# archived_issues_collector

- 此项目用于收集各个**归档文件**并根据**指定的版本号范围**来**汇总归档内容并重新格式化输出**为ChangeLog形式的内容
- 本项目的预期设计触发条件是通过github action流水线手动触发来运行,详见 [ChangeLog输出流水线使用指南](./ChangeLog输出流水线使用指南.md)
- 本项目还支持通过命令行参数传入版本号范围以及配置文件路径来本地运行
- 运行项目需要python解释器版本 >= `3.10`

## 配置文件变量

- 配置文件位于 [config/config.json](config/config.json)

| 变量名                                           | 类型                | 默认值 | 描述                                                                                                                                                                                                                            |
| ------------------------------------------------ | ------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| archived_issues_info                             | list[dict[str,Any]] | []     | 定义归档文件源获取规则,目前只支持http和https源                                                                                                                                                                                  |
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


## 项目结构

- `src/` 业务代码目录
- `tests/` 单元测试代码目录
- `config/` 配置文件目录
- `dev-requirements.txt/` 项目所需第三方库的定义,开发前使用
- `requirements.txt/` 项目所需第三方库的定义,流水线运行前使用
