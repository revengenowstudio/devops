import os

from archive_document import ArchiveDocument
from json_config import Config
from config_data_source import JsonConfigDataSource, EnvConfigDataSource
from archive_document_collector import ArchiveDocumentCollector
from get_args import get_value_from_args
from log import Log
from exception import *


def main():

    # 从各种地方读配置文件和输入内容
    config_path = get_value_from_args(
        "-c",
        "--config",
    )
    if config_path is None:
        print(Log.config_path_not_found)
        return

    config = Config()
    EnvConfigDataSource().load(config)
    JsonConfigDataSource(config_path).load(config)

    # 拉取归档文件内容
    archive_document_collector = ArchiveDocumentCollector(
        config.repository_token
    )
    document_content_list: list[str] = []
    for archived_issues_info in config.archived_issues_info:
        archived_issues_info.use_token
        document_content: str = archive_document_collector.collect_document(
            url=archived_issues_info.url,
            json_api=archived_issues_info.json_api,
            content_key=archived_issues_info.content_key,
            base64_decode=archived_issues_info.base64_decode,
            use_token=archived_issues_info.use_token,
            http_headers=archived_issues_info.http_headers,
        )
        document_content_list.append(document_content)

    # 查找符合版本号范围的内容
    target_lines: list[str] = []
    for document_content in document_content_list:
        archive_document = ArchiveDocument()
        archive_document.loads(
            document_content,
            config.archive_document.skip_header_rows
        )

        target_lines.extend(
            archive_document.search_line_in_version_range(
                version_start_str=config.version_start,
                version_end_str=config.version_end,
                table_separator=config.archive_document.table_separator,
                archived_version_column_index=config.archive_document.archived_version_column_index,
            )
        )

    # 将结果写入文件中
    with open(config.output_path, "w", encoding="utf-8") as file:
        file.writelines(target_lines)


if __name__ == '__main__':
    main()
