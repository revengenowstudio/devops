from dataclasses import dataclass, field
from typing import TypeAlias

IssueType: TypeAlias = str


@dataclass
class Config:
    @dataclass
    class ArchivedIssuesInfo:
        url: str = str()
        json_api: bool = False
        content_key: str = str()
        base64_decode: bool = False
        use_token: bool = False
        http_headers: dict[str, str] = field(default_factory=dict)

    @dataclass
    class RawLinePicker:
        column_index: int = 0
        pick_types: list[str] = field(default_factory=list)
        regex: str | None = None

    @dataclass
    class ArchivedDocument:
        skip_header_rows: int = 0
        table_separator: str = str()
        reformat_template: str = str()
        raw_line_pickers: list["Config.RawLinePicker"] = field(default_factory=list)

    # 从env读取
    # repository_token: str = str()
    # version_start: str = str()
    # version_end: str = str()

    # 从命令行参数读取
    config_path: str = str()
    repository_token: str = str()
    version_start: str = str()
    version_end: str = str()
    ignore_introduce_version: bool = True
    include_start_version: bool = True
    include_end_version: bool = False

    # 从配置文件json读取
    archived_issues_info: list[ArchivedIssuesInfo] = field(
        default_factory=list[ArchivedIssuesInfo]
    )
    archive_document: ArchivedDocument = field(default_factory=ArchivedDocument)
    output_path: str = str()
