import re
from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict

from exception import (PickerNotFoundError, ErrorMessage,
                       ReformatLineError, SearchLineError)
from log import Log
from version_code import VersionCode
from json_config import Config


class PickerType():
    first_number = "first_number"
    issue_type = "issue_type"
    issue_title = "issue_title"
    issue_location = "issue_location"
    introduce_version = "introduce_version"
    archived_version = "archived_version"


class IssueInfo(TypedDict):
    first_number: str
    issue_type: str
    issue_title: str
    issue_location: str
    issue_url: str
    introduce_version: str
    archived_version: str


class ArchiveDocument():

    @property
    def new_line_length(self) -> int:
        return len(self.__new_line)

    def __init__(self):
        self.__lines: list[str] = []
        self.__new_line: list[str] = []

    def __split_line(self,
                     line: str,
                     table_separator: str
                     ) -> list[str]:
        result = [i for i in line.split(table_separator)
                  if i.strip()]
        if len(result) == 1:
            raise ValueError(
                ErrorMessage.incorrect_line_format
                .format(
                    table_separator=table_separator
                )
            )
        return result

    def __apply_single_picker(
        self,
        column: list[str],
        picker: Config.RawLinePicker
    ) -> list[str]:
        try:
            if picker.regex is None:
                return [column[picker.column_index]]
            return re.findall(
                picker.regex,
                column[picker.column_index]
            )
        except IndexError:
            raise IndexError(
                ErrorMessage.column_index_out_of_range
                .format(
                    picker=picker
                ),
            )

    def __apply_all_picker(
        self,
        column: list[str],
        pickers: list[Config.RawLinePicker]
    ) -> IssueInfo:
        result = {}
        for picker in pickers:
            try:
                if picker.regex is None:
                    result[picker.pick_types[0]] = column[picker.column_index]
                else:
                    for pick_types, value in zip(
                        picker.pick_types,
                        re.findall(
                            picker.regex,
                            column[picker.column_index]
                        )[0]
                    ):
                        value: str
                        result[pick_types] = value.strip()
            except IndexError:
                raise IndexError(
                    ErrorMessage.column_index_out_of_range
                    .format(
                        picker=picker
                    )
                )
        if result.get("issue_url") is None:
            result["issue_url"] = ""
        return IssueInfo(**result)

    def __select_picker(
        self,
        target_pick_type: str,
        pickers: list[Config.RawLinePicker]
    ) -> Config.RawLinePicker:
        for picker in pickers:
            if target_pick_type in picker.pick_types:
                return picker
        raise PickerNotFoundError(
            ErrorMessage.picker_not_found
            .format(
                picker_type=target_pick_type
            )
        )

    def loads(self,
              raw_content: str,
              skip_header_rows: int):
        all_lines = raw_content.splitlines(keepends=True)
        self.__lines = [i for i in all_lines[skip_header_rows:]
                        if i.strip()]

    def search_line_in_version_range(
        self,
        version_start_str: str,
        version_end_str: str,
        table_separator: str,
        raw_line_pickers: list[Config.RawLinePicker],
        match_introduce_version: bool,
    ) -> None:
        all_lines = self.__lines
        version_start = VersionCode(version_start_str)
        version_end = VersionCode(version_end_str)
        result: list[str] = []
        for line_index, line in enumerate(all_lines):
            try:
                column = self.__split_line(line, table_separator)
                archived_version = VersionCode(
                    self.__apply_single_picker(
                        column,
                        self.__select_picker(
                            PickerType.archived_version,
                            raw_line_pickers
                        )
                    )[0]
                )
                version_matched = version_start <= archived_version <= version_end

                if (not version_matched
                        and match_introduce_version):
                    introduce_version = VersionCode(
                        self.__apply_single_picker(
                            column,
                            self.__select_picker(
                                PickerType.introduce_version,
                                raw_line_pickers
                            )
                        )[0]
                    )
                    version_matched = version_start <= introduce_version <= version_end

                if version_matched:
                    result.append(line)

            except Exception as exc:
                print(
                    ErrorMessage.error_in_search_lines
                    .format(
                        line_index=line_index + 1,
                        line=line,
                        exc=exc
                    )
                )

        self.__new_line = result

    def reformat_lines(
        self,
        table_separator: str,
        raw_line_pickers: list[Config.RawLinePicker],
        reformat_template: str
    ) -> None:
        raw_lines = self.__new_line
        reformat_lines: list[str] = []
        for line in raw_lines:
            try:
                column = self.__split_line(line, table_separator)
                issue_info = self.__apply_all_picker(column, raw_line_pickers)
                issue_url_parents = issue_info["issue_url"]
                md_link_square_start = ""
                md_link_square_end = ""
                if issue_info["issue_url"] != "":
                    issue_url_parents = f'({issue_url_parents})'
                    md_link_square_start = '['
                    md_link_square_end = ']'

                reformat_lines.append(
                    reformat_template.format(
                        md_link_square_start=md_link_square_start,
                        md_link_square_end=md_link_square_end,
                        issue_url_parents=issue_url_parents,
                        **issue_info
                    )
                )
            except Exception as exc:
                print(
                    ErrorMessage.reformat_line_error
                    .format(
                        line=line,
                        exc=exc
                    )
                )
        self.__new_line = reformat_lines

    def add_brake_line(self) -> None:
        self.__new_line = [
            i if i.endswith("\n") else i + "\n"
            for i in self.__new_line
        ]

    def write_line_file(self,
                        output_path_str: str) -> None:
        new_line = self.__new_line
        output_path = Path(output_path_str)
        print(Log.write_content_to
              .format(path=output_path))
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as file:
                file.writelines(new_line)
        except Exception as exc:
            print(ErrorMessage.write_file_error
                  .format(exc=exc))
        print(Log.write_content_success
              .format(path=output_path))

    def show_lines(self) -> list[str]:
        return self.__lines.copy()

    def add_new_line(self, line: str) -> None:
        '''不建议直接使用此方法'''
        self.__lines.append(line)
