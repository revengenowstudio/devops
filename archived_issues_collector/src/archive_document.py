import re
from dataclasses import dataclass
from typing import TypedDict

from exception import PickerNotFoundError, ErrorMessage
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

    def __init__(self):
        self.__lines: list[str] = []

    def __split_line(self,
                     line: str,
                     table_separator: str
                     ) -> list[str]:
        return [i for i in line.split(table_separator)
                if i.strip()]

    def __apply_single_picker(
        self,
        column: list[str],
        picker: Config.RawLinePicker
    ) -> list[str]:
        if picker.regex is None:
            return [column[picker.column_index]]
        return re.findall(
            picker.regex,
            column[picker.column_index]
        )

    def __apply_all_picker(
        self,
        column: list[str],
        pickers: list[Config.RawLinePicker]
    ) -> IssueInfo:
        result = {}
        for picker in pickers:
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
    ) -> list[str]:
        all_lines = self.__lines
        version_start = VersionCode(version_start_str)
        version_end = VersionCode(version_end_str)
        result: list[str] = []
        for line in all_lines:
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

        return result

    def reformat_lines(
        self,
        lines: list[str],
        table_separator: str,
        raw_line_pickers: list[Config.RawLinePicker],
        reformat_template: str
    ) -> list[str]:
        raw_lines = lines
        reformat_lines: list[str] = []
        for line in raw_lines:
            column = self.__split_line(line, table_separator)
            issue_info = self.__apply_all_picker(column, raw_line_pickers)
            issue_url_parents = issue_info["issue_url"]
            if issue_info["issue_url"] != "":
                issue_url_parents = f'({issue_url_parents})'

            reformat_lines.append(
                reformat_template.format(
                    issue_url_parents=issue_url_parents,
                    **issue_info
                )
            )
        return reformat_lines

    def add_brake_line(self, lines: list[str]) -> list[str]:
        return [i if i.endswith("\n") else i + "\n"
                for i in lines]

    def show_lines(self) -> list[str]:
        return self.__lines.copy()

    def add_new_line(self, line: str) -> None:
        '''不建议直接使用此方法'''
        self.__lines.append(line)
