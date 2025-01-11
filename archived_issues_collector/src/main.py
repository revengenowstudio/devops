import sys
from archive_document import ArchiveDocument
from json_config import Config
from config_data_source import (JsonConfigDataSource,
                                ArgsConfigDataSource,
                                EnvConfigDataSource)
from archive_document_collector import ArchiveDocumentCollector
from get_args import should_args_exist
from log import Log
from version_code import VersionCode
from exception import *


def main():

    if (should_args_exist(
        short_arg="--help",
        long_arg="-h"
    ) or len(sys.argv) == 1):
        print(Log.help_message)
        exit(0)

    # 从各种地方读配置文件和输入内容
    config = Config()
    ArgsConfigDataSource().load(config)
    EnvConfigDataSource().load(config)
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

    for index, archived_issues_info in enumerate(config.archived_issues_info):
        index_ = index + 1
        try:
            print(
                Log.getting_something_from
                .format(
                    another=Log.archived_source
                    .format(index=index_),
                    something=Log.archived_content
                ))
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
                    another=Log.archived_source
                    .format(index=index_),
                    something=Log.archived_content
                ))
        except Exception as exc:
            print(
                ErrorMessage.collect_document_error
                .format(
                    index=index_,
                    exc=str(exc)
                )
            )
    print(
        Log.collect_document_success_number
        .format(
            number=len(document_content_list)
        )
    )

    # 查找符合版本号范围的内容,并将内容重新格式化
    archive_document = ArchiveDocument()
    print(Log.match_archive_content_in_version_range)
    for document_content in document_content_list:
        archive_document.loads(
            document_content,
            config.archive_document.skip_header_rows
        )
        archive_document.search_line_in_version_range(
            version_start_str=config.version_start,
            version_end_str=config.version_end,
            table_separator=config.archive_document.table_separator,
            raw_line_pickers=config.archive_document.raw_line_pickers,
            match_introduce_version=config.match_introduce_version,
            include_start_version=config.include_start_version,
            include_end_version=config.include_end_version
        )
        print(Log.match_much_archive_content
              .format(
                  count=archive_document.new_line_length
              ))
        archive_document.reformat_lines(
            table_separator=config.archive_document.table_separator,
            raw_line_pickers=config.archive_document.raw_line_pickers,
            reformat_template=config.archive_document.reformat_template
        )
        archive_document.add_brake_line()

        # 将结果写入文件中
        archive_document.write_line_file(config.output_path)

    print(Log.job_done)


if __name__ == '__main__':
    main()
