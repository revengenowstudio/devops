from dataclasses import dataclass
import re

from version_code import VersionCode


issue_location_regex = re.compile(r"\[[内外]部Issue#.+?\]")


@dataclass
class VersionMatchStatistics:
    line: str
    introduce_version: VersionCode
    archived_version: VersionCode
    in_target_version_range: bool

    def issue_location(self) -> str:
        if match := issue_location_regex.search(self.line):
            return match[0].strip()
        return "Unknown Issue Location"


class IssueStatisticsTool:
    def __init__(self):
        self._stat_lists: list[VersionMatchStatistics] = []

    def append_version_match_statistics(
        self, match_result: VersionMatchStatistics
    ) -> None:
        self._stat_lists.append(match_result)

    def to_lines(self) -> str:
        if not self._stat_lists:
            return "\n匹配统计信息: \n(无数据)"

        result: list[str] = ["\n匹配统计信息: "]
        max_intro = max(len(str(stat.introduce_version)) for stat in self._stat_lists)
        max_arch = max(len(str(stat.archived_version)) for stat in self._stat_lists)

        result.extend(
            [
                f"{stat.issue_location().ljust(15)} | 引入版本: {str(stat.introduce_version).ljust(max_intro)} | 归档版本: {str(stat.archived_version).ljust(max_arch)} | 匹配结果: {stat.in_target_version_range}"
                for stat in self._stat_lists
            ]
        )
        return "\n".join(result)
