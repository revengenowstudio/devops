import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypedDict

from exception import (
    PickerNotFoundError,
    ErrorMessage,
    ReformatLineError,
    SearchLineError,
)
from log import Log
from version_code import VersionCode
from json_config import Config


class PickerType:
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


def extent_double_list(input: list[list[Any]]) -> list[Any]:
    result = []
    for deep_list in input:
        for item in deep_list:
            result.append(item)
    return result


class ArchiveDocument:
    @property
    def new_line_length(self) -> int:
        return len(self.__new_lines)

    def __init__(self):
        self.__lines: list[str] = []
        self.__new_lines: list[str] = []

    def __split_line(self, line: str, table_separator: str) -> list[str]:
        result = []
        for index, item in enumerate(line.split(table_separator)):
            if (
                index == 0 or index == (len(line.split(table_separator)) - 1)
            ) and item.strip() == "":
                continue
            result.append(item.strip())
        if len(result) == 1:
            raise ValueError(
                ErrorMessage.incorrect_line_format.format(
                    table_separator=table_separator
                )
            )
        return result

    def __apply_single_picker(
        self, column: list[str], picker: Config.RawLinePicker
    ) -> list[str]:
        try:
            if picker.regex is None:
                return [column[picker.column_index]]
            result = re.findall(picker.regex, column[picker.column_index])
            if all([isinstance(i, tuple) for i in result]):
                return extent_double_list(result)
            return result
        except IndexError:
            raise IndexError(
                ErrorMessage.column_index_out_of_range.format(
                    column_number=len(column),
                    column_index=picker.column_index,
                    picker=picker,
                ),
            )

    def __apply_all_picker(
        self, column: list[str], pickers: list[Config.RawLinePicker]
    ) -> IssueInfo:
        result = {}
        for picker in pickers:
            try:
                if picker.regex is None:
                    result[picker.pick_types[0]] = column[picker.column_index]
                else:
                    findall_result = re.findall(
                        picker.regex, column[picker.column_index]
                    )
                    if all([isinstance(i, tuple) for i in findall_result]):
                        findall_result = extent_double_list(findall_result)
                    for pick_types, value in zip(picker.pick_types, findall_result):
                        value: str
                        result[pick_types] = value.strip()
            except IndexError:
                raise IndexError(
                    ErrorMessage.column_index_out_of_range.format(
                        column_number=len(column),
                        column_index=picker.column_index,
                        picker=picker,
                    )
                )
        if result.get("issue_url") is None:
            result["issue_url"] = ""
        return IssueInfo(**result)

    def __select_picker(
        self, target_pick_type: str, pickers: list[Config.RawLinePicker]
    ) -> Config.RawLinePicker:
        for picker in pickers:
            if target_pick_type in picker.pick_types:
                return picker
        raise PickerNotFoundError(
            ErrorMessage.picker_not_found.format(picker_type=target_pick_type)
        )

    def loads(self, raw_content: str, skip_header_rows: int):
        all_lines = raw_content.splitlines(keepends=True)
        self.__lines = [i for i in all_lines[skip_header_rows:] if i.strip()]

    def should_version_in_range(
        self,
        version_start: VersionCode,
        version_end: VersionCode,
        target_version: VersionCode,
        include_start_version: bool,
        include_end_version: bool,
    ) -> bool:
        is_within_start = False
        is_within_end = False

        if include_start_version:
            is_within_start = target_version >= version_start
        else:
            is_within_start = target_version > version_start

        if include_end_version:
            is_within_end = target_version <= version_end
        else:
            is_within_end = target_version < version_end

        return is_within_start and is_within_end

    def search_line_in_version_range(
        self,
        version_start_str: str,
        version_end_str: str,
        table_separator: str,
        raw_line_pickers: list[Config.RawLinePicker],
        match_introduce_version: bool,
        include_start_version: bool,
        include_end_version: bool,
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
                            PickerType.archived_version, raw_line_pickers
                        ),
                    )[0]
                )
                version_matched = self.should_version_in_range(
                    version_start,
                    version_end,
                    archived_version,
                    include_start_version,
                    include_end_version,
                )

                if not version_matched and match_introduce_version:
                    introduce_version = VersionCode(
                        self.__apply_single_picker(
                            column,
                            self.__select_picker(
                                PickerType.introduce_version, raw_line_pickers
                            ),
                        )[0]
                    )
                    version_matched = self.should_version_in_range(
                        version_start,
                        version_end,
                        introduce_version,
                        include_start_version,
                        include_end_version,
                    )

                if version_matched:
                    result.append(line)

            except Exception as exc:
                print(
                    ErrorMessage.error_in_search_lines.format(
                        line_index=line_index + 1, line=line, exc=exc
                    )
                )

        self.__new_lines = result

    def reformat_lines(
        self,
        table_separator: str,
        raw_line_pickers: list[Config.RawLinePicker],
        reformat_template: str,
    ) -> None:
        raw_lines = self.__new_lines
        reformat_lines: list[str] = []
        for line in raw_lines:
            try:
                column = self.__split_line(line, table_separator)
                issue_info = self.__apply_all_picker(column, raw_line_pickers)
                issue_url_parents = issue_info["issue_url"]
                md_link_square_start = ""
                md_link_square_end = ""
                if issue_info["issue_url"] != "":
                    issue_url_parents = f"({issue_url_parents})"
                    md_link_square_start = "["
                    md_link_square_end = "]"

                reformat_lines.append(
                    reformat_template.format(
                        md_link_square_start=md_link_square_start,
                        md_link_square_end=md_link_square_end,
                        issue_url_parents=issue_url_parents,
                        **issue_info,
                    )
                )
            except Exception as exc:
                print(ErrorMessage.reformat_line_error.format(line=line, exc=exc))
        self.__new_lines = reformat_lines

    def add_brake_line(self) -> None:
        self.__new_lines = [
            i if i.endswith("\n") else i + "\n" for i in self.__new_lines
        ]

    def write_line_file(self, output_path_str: str) -> None:
        new_line = self.__new_lines
        output_path = Path(output_path_str)
        print(Log.write_content_to.format(path=output_path))
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "a", encoding="utf-8") as file:
                file.writelines(new_line)
        except Exception as exc:
            print(ErrorMessage.write_file_error.format(exc=exc))
        print(Log.write_content_success.format(path=output_path))

    def show_lines(self) -> list[str]:
        return self.__lines.copy()

    def show_new_lines(self) -> list[str]:
        return self.__new_lines.copy()

    def add_new_line(self, line: str) -> None:
        """不建议直接使用此方法"""
        self.__new_lines.append(line)
