from log import Log


class ArchiveDocument():
    def __init__(self):
        self.__path: str
        self.__lines: list[str] = []
        self.__new_lines: list[str] = []
        self.__reverse_lines: list[str] = []
        self.__lines_set: set[str] = set()

    def file_load(self, path: str):
        print(Log.getting_something_from
              .format(another=path,
                      something=Log.archive_document_content))
        self.__path = path
        with open(path, 'r', encoding="utf-8") as file:
            self.__lines = file.readlines()
            self.__reverse_lines = self.__lines[::-1]
            self.__lines_set = set(self.__lines)
        print(Log.getting_something_from_success
              .format(another=path,
                      something=Log.archive_document_content))

    def show_new_line(self) -> list[str]:
        return self.__new_lines.copy()

    def show_lines(self) -> list[str]:
        return self.__lines.copy()

    def add_new_line(self, line: str) -> None:
        '''不建议直接使用此方法，建议使用archive_issue来格式化issue内容'''
        self.__add_line(line)

    def __add_line(self, line: str) -> None:
        print(Log.add_new_line)
        self.__new_lines.append(line)

    def __replace_line(self, index: int, line: str) -> None:
        print(Log.replaced_line_index
              .format(line_index=index,
                      ))
        self.__lines[index] = line

    def __get_table_last_line_index(self) -> int:
        # 后面的写入到归档文件函数会把归档序号+1，所以这里得0
        line_index = 0
        for index, line in enumerate(self.__reverse_lines, 1):
            if line.strip():
                line_index = index
                break
        return len(self.__lines) - line_index

    @staticmethod
    def __find_table_number_in_line(
        line: str,
        table_separator: str
    ) -> int:
        result = 0
        start = line.find(table_separator)
        end = line.find(table_separator, start+1)
        if (temp := line[start+1:end]).isdigit():
            print(Log.got_archive_number
                  .format(
                      archive_number=temp
                  ))
            result = int(temp)
        else:
            print(Log.unexpected_archive_number
                  .format(
                      default_number=result + 1,
                      line=line
                  ))
        return result

    def __get_last_table_number(
        self,
        table_separator: str
    ) -> int:
        return self.__get_table_number_by_line_index(
            self.__get_table_last_line_index(),
            table_separator
        )

    def should_issue_record_exists(
        self,
        issue_repository: str,
        issue_id: int,
    ) -> bool:
        sub_string = f'{issue_repository}#{issue_id}]'
        for line in self.__lines_set:
            if sub_string in line:
                print(
                    Log.issue_id_found_in_archive_record
                    .format(issue_id=issue_id)
                )
                return True
        print(
            Log.issue_id_not_found_in_archive_record
            .format(issue_id=issue_id)
        )
        return False

    def __get_table_number_by_line_index(
        self,
        line_index: int,
        table_separator: str
    ) -> int:
        return self.__find_table_number_in_line(
            self.__lines[line_index],
            table_separator
        )

    def __find_line_index_by_issue_id(
            self,
            issue_id: int,
            issue_repository: str
    ) -> int:
        '''O(n)查询速度去根据记录中匹配issue_id的行号
        查不到会返回 -1
        '''
        # 虽然这里是 O(n) 的查询速度
        # 但是我相信归档文件不会有10万行的内容的
        sub_string = f'{issue_repository}#{issue_id}'
        for index, line in enumerate(self.__lines):
            if sub_string in line:
                print(Log.issue_id_found_in_archive_record
                      .format(issue_id=issue_id))
                return index
        print(Log.issue_id_not_found_in_archive_record
              .format(issue_id=issue_id))
        return -1

    def save(self) -> None:
        print(Log.write_content_to_document)
        if not self.__lines[-1].endswith('\n'):
            self.__lines[-1] += "\n"
        if len(self.__new_lines) != 0:
            self.__lines.insert(
                self.__get_table_last_line_index() + 1,
                *self.__new_lines
            )
        with open(self.__path, 'w', encoding="utf-8") as file:
            file.writelines(self.__lines)
        print(Log.write_content_to_document_success)
