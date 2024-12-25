import pytest
from unittest.mock import patch, MagicMock

from src.archive_document import ArchiveDocument


class TestArchiveDocument():

    @pytest.mark.parametrize(
        "test_lines, expected_result,skip_header_rows",
        [
            ("test_lines\n111\n \n\n   \n\n \n  \n",
             ['test_lines\n', '111\n'],
                0
             ),
            ("test_lines\n111\n \n\n   \n\n \n123\n",
             ['123\n'],
                2
             )
        ]
    )
    def test_loads(self,
                   test_lines: str,
                   expected_result: list[str],
                   skip_header_rows: int,
                   ):

        document = ArchiveDocument()
        document.loads(
            raw_content=test_lines,
            skip_header_rows=skip_header_rows
        )
        assert document.show_lines() == expected_result
        
    def test_search_line_in_version_range(
        self,
    ):
        # TODO 没写完
        pass
