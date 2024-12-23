from pathlib import Path

from archive_document import ArchiveDocument
from json_config import Config
from config_data_source import JsonConfigDataSource, ArgsConfigDataSource
from archive_document_collector import ArchiveDocumentCollector
from log import Log
from version_code import VersionCode
from exception import *


def main():

    # 从各种地方读配置文件和输入内容
    config = Config()
    ArgsConfigDataSource().load(config)
    JsonConfigDataSource(config.config_path).load(config)

    # 版本号是否合法
    for name, version in zip(
        (Log.version_start, Log.version_end),
            (config.version_start, config.version_end)):
        try:
            VersionCode.should_version_valid(version)
        except ValueError as exc:
            raise ValueError(f'"{name}" {str(exc)}')

    # 拉取归档文件内容
    archive_document_collector = ArchiveDocumentCollector(
        config.repository_token
    )
    document_content_list: list[str] = []
    print(
        Log.getting_something_from
        .format(
            another=Log.archived_source,
            something=Log.archived_content
        ))
    for archived_issues_info in config.archived_issues_info:
        archived_issues_info.use_token
        document_content: str = archive_document_collector.collect_document(
            url=archived_issues_info.url,
            content_key=archived_issues_info.content_key,
            http_headers=archived_issues_info.http_headers,
            json_api=archived_issues_info.json_api,
            base64_decode=archived_issues_info.base64_decode,
            use_token=archived_issues_info.use_token,
        )
        document_content_list.append(document_content)
    print(
        Log.getting_something_from_success
        .format(
            another=Log.archived_source,
            something=Log.archived_content
        ))

    # 查找符合版本号范围的内容
    target_lines: list[str] = []
    print(Log.match_archive_content_in_version_range)
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
                introduce_version_column_index=config.archive_document.introduce_version_column_index,
                archived_version_column_index=config.archive_document.archived_version_column_index,
                match_introduce_version=config.match_introduce_version
            )
        )
    print(Log.match_much_archive_content
          .format(
              count=len(archive_document.show_lines())
          ))

    # 将结果写入文件中

    output_path = Path(config.output_path)
    print(Log.write_content_to
          .format(path=output_path))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as file:
        file.writelines(target_lines)

    print(Log.job_done)


if __name__ == '__main__':
    main()
