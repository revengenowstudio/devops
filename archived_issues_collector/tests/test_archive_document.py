from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.archive_document import ArchiveDocument
from src.version_code import VersionCode
from src.json_config import Config


class TestArchiveDocument:
    @pytest.fixture(scope="function")
    def archive_document(self) -> ArchiveDocument:
        return ArchiveDocument()

    @pytest.mark.parametrize(
        "test_lines, expected_result,skip_header_rows",
        [
            ("test_lines\n111\n \n\n   \n\n \n  \n", ["test_lines\n", "111\n"], 0),
            ("test_lines\n111\n \n\n   \n\n \n123\n", ["123\n"], 2),
        ],
    )
    def test_loads(
        self,
        test_lines: str,
        expected_result: list[str],
        skip_header_rows: int,
        archive_document: ArchiveDocument,
    ):
        archive_document.loads(
            raw_content=test_lines, skip_header_rows=skip_header_rows
        )
        assert archive_document.show_lines() == expected_result

    def test_search_line_in_version_range(self, archive_document: ArchiveDocument):
        pickers: list[Config.RawLinePicker] = [
            Config.RawLinePicker(
                column_index=2, pick_types=["introduce_version"], regex=None
            ),
            Config.RawLinePicker(
                column_index=3, pick_types=["archived_version"], regex=None
            ),
        ]
        table_separator = "|"
        version_start_str = "0.99.915"
        version_end_str = "0.99.920"
        line1 = "|3|(Bug修复)修复了在攻城拔寨模式中，科技防空堡垒只能对正前方开火 [外部Issue#103] |0.99.915|0.99.919|"
        line2 = "|4|(Bug修复)调整了恐怖机器人的攻击射程 [外部Issue#105]  |0.99.919  | 0.99.921|"
        useless_string = "\njidoqj|iaohdoqweq\n"
        line3 = "|7|(设定调整)英国圣骑士机甲无人操控时不能被神经毒气影响  [外部Issue#831](https://example.com) ||0.99.919|"
        line4 = "|4|(设定引入)【合作任务】生化合作任务1-无人生还 任务设计与制作                                  [内部Issue#414](https://example.com/-/issues/414) ||0.99.916b2|"
        raw_content = "\n".join([line1, line2, useless_string, line3, line4])

        archive_document.loads(raw_content=raw_content, skip_header_rows=0)
        archive_document.search_line_in_version_range(
            version_start_str=version_start_str,
            version_end_str=version_end_str,
            table_separator=table_separator,
            raw_line_pickers=pickers,
            ignore_introduce_version=True,
            include_start_version=True,
            include_end_version=True,
        )
        assert archive_document.show_new_lines()[0].strip() == line1
        assert archive_document.show_new_lines()[1].strip() == line3
        assert archive_document.show_new_lines()[2].strip() == line4

        archive_document.search_line_in_version_range(
            version_start_str=version_start_str,
            version_end_str=version_end_str,
            table_separator=table_separator,
            raw_line_pickers=pickers,
            ignore_introduce_version=False,
            include_start_version=True,
            include_end_version=True,
        )
        assert archive_document.show_new_lines()[1].strip() == line2

    def test_reformat_lines(self, archive_document: ArchiveDocument):
        pickers = [
            Config.RawLinePicker(
                column_index=0, pick_types=["first_number"], regex=None
            ),
            Config.RawLinePicker(
                column_index=1,
                pick_types=["issue_type", "issue_title", "issue_location", "issue_url"],
                regex="\\((.*?)\\)(.*)\\[(.*?)\\]{1}\\(?(.+(?=\\)))?",
            ),
        ]
        table_separator = "|"
        reformat_template = """[{issue_type}({md_link_square_start}{issue_location}{md_link_square_end}{issue_url_parents})]  {issue_title}
        """

        line1 = "|3   |(Bug修复)修复了在攻城拔寨模式中，科技防空堡垒只能对正前方开火 [外部Issue#103](https://example.com) |0.99.915| 0.99.919|"
        line2 = "|4   |(Bug修复)调整了恐怖机器人的攻击射程 [外部Issue#105]  |0.99.919  | 0.99.921|"
        useless_string = "\njidoqj|iaohdoqweq\n"
        line3 = "|4|(设定引入)【合作任务】生化合作任务1-无人生还 任务设计与制作                                  [内部Issue#414](https://example.com/-/issues/414) ||0.99.916b2|"
        for i in [line1, line2, useless_string, line3]:
            archive_document.add_new_line(i + "\n")

        archive_document.reformat_lines(
            table_separator=table_separator,
            raw_line_pickers=pickers,
            reformat_template=reformat_template,
        )
        assert archive_document.show_new_lines()[0].strip() == (
            "[Bug修复([外部Issue#103](https://example.com))]  修复了在攻城拔寨模式中，科技防空堡垒只能对正前方开火"
        )
        assert archive_document.show_new_lines()[1].strip() == (
            "[Bug修复(外部Issue#105)]  调整了恐怖机器人的攻击射程"
        )
        assert archive_document.show_new_lines()[2].strip() == (
            "[设定引入([内部Issue#414](https://example.com/-/issues/414))]  【合作任务】生化合作任务1-无人生还 任务设计与制作"
        )

    @pytest.mark.parametrize(
        "version_start,version_end,target_version,include_start_version,include_end_version,expected_result",
        [
            ("0.99.916", "0.99.918", "0.99.916", False, False, False),
            ("0.99.916", "0.99.918", "0.99.918", False, False, False),
            ("0.99.916", "0.99.918", "0.99.917", False, False, True),
            ("0.99.916", "0.99.918", "0.99.916", True, False, True),
            ("0.99.916", "0.99.918", "0.99.918", True, False, False),
            ("0.99.916", "0.99.918", "0.99.917", True, False, True),
            ("0.99.916", "0.99.918", "0.99.916", False, True, False),
            ("0.99.916", "0.99.918", "0.99.918", False, True, True),
            ("0.99.916", "0.99.918", "0.99.917", False, True, True),
            ("0.99.916", "0.99.918", "0.99.916", True, True, True),
            ("0.99.916", "0.99.918", "0.99.918", True, True, True),
            ("0.99.916", "0.99.918", "0.99.917", True, True, True),
        ],
    )
    def test_should_version_in_range(
        self,
        archive_document: ArchiveDocument,
        version_start: str,
        version_end: str,
        target_version: str,
        include_start_version: bool,
        include_end_version: bool,
        expected_result: bool,
    ):
        assert (
            archive_document.should_version_in_range(
                version_start=VersionCode(version_start),
                version_end=VersionCode(version_end),
                target_version=VersionCode(target_version),
                include_start_version=include_start_version,
                include_end_version=include_end_version,
            )
            == expected_result
        )

    def test_add_brake_line(self, archive_document: ArchiveDocument):
        line1 = "123"
        line2 = "124"
        archive_document.add_new_line(line1)
        archive_document.add_new_line(line2)

        archive_document.add_brake_line()

        assert archive_document.show_new_lines()[0] == f"{line1}\n"
        assert archive_document.show_new_lines()[1] == f"{line2}\n"

    def test_write_line_file(self, archive_document: ArchiveDocument, tmpdir: Path):
        line1 = "123\n"
        line2 = "124"
        archive_document.add_new_line(line1)
        archive_document.add_new_line(line2)

        output_path = tmpdir / "test.md"

        archive_document.write_line_file(str(output_path))

        assert output_path.read_text(encoding="utf-8") == line1 + line2
