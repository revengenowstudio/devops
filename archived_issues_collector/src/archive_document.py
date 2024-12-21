from log import Log
from version_code import VersionCode, VersionType


class ArchiveDocument():
    def __init__(self):
        self.__lines: list[str] = []

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
        archived_version_column_index: int,
    ) -> list[str]:
        all_lines = self.__lines
        version_start = VersionCode(version_start_str)
        version_end = VersionCode(version_end_str)
        result: list[str] = []
        for line in all_lines:
            row = [i for i in line.split(table_separator)
                   if i.strip()]
            archived_version = VersionCode(
                row[archived_version_column_index])
            if version_start <= archived_version <= version_end:
                result.append(line)
        return result

    def show_lines(self) -> list[str]:
        return self.__lines.copy()

    def add_new_line(self, line: str) -> None:
        '''不建议直接使用此方法'''
        self.__lines.append(line)
