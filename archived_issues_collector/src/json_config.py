from dataclasses import dataclass, field
from typing import TypedDict, TypeAlias

IssueType: TypeAlias = str


class ArchivedIssuesInfoJson(TypedDict):
    url: str
    json_api: bool
    content_key: str
    base64_decode: bool
    use_token: bool
    http_headers: dict[str, str]


class ArchivedDocumentJson(TypedDict):
    skip_header_rows: int
    table_separator: str
    skip_header_rows: int


class ConfigJson(TypedDict):
    archived_issues_info: list[ArchivedIssuesInfoJson]
    archive_document: ArchivedDocumentJson
    output_path: str


@dataclass
class Config():
    @dataclass
    class ArchivedIssuesInfo():
        url: str = str()
        json_api: bool = False
        content_key: str = str()
        base64_decode: bool = False
        use_token: bool = False
        http_headers: dict[str, str] = field(
            default_factory=dict)

    @dataclass
    class ArchivedDocument():
        skip_header_rows: int = 0
        table_separator: str = str()
        introduce_version_column_index: int = 0
        archived_version_column_index: int = 0

    # 从env读取
    # repository_token: str = str()
    # version_start: str = str()
    # version_end: str = str()

    # 从命令行参数读取
    config_path: str = str()
    repository_token: str = str()
    version_start: str = str()
    version_end: str = str()
    match_introduce_version: bool = False

    # 从配置文件json读取
    archived_issues_info: list[ArchivedIssuesInfo] = field(
        default_factory=list[ArchivedIssuesInfo])
    archive_document: ArchivedDocument = field(
        default_factory=ArchivedDocument)
    output_path: str = str()
