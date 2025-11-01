import pytest

from src.config_checker import *


class TestConfigChecker:
    def test_register(self):
        ConfigChecker._registered_functions = set()

        def test_func(x: dict[str, str]) -> None:
            return None

        ConfigChecker.register(test_func)
        assert len(ConfigChecker._registered_functions) == 1

        ConfigChecker.register(test_func)
        ConfigChecker.register(test_func)
        assert len(ConfigChecker._registered_functions) == 1


@pytest.mark.parametrize(
    "test_config,exception",
    [
        ({"archive_document": {"raw_line_pickers": []}}, None),
        (
            {
                "archive_document": {
                    "raw_line_pickers": [
                        {
                            "column_index": 0,
                            "pick_types": [
                                "first_number1",
                                "first_number2",
                            ],
                            "regex": None,
                        }
                    ]
                }
            },
            ValueError,
        ),
        (
            {
                "archive_document": {
                    "raw_line_pickers": [
                        {"column_index": 0, "pick_types": [], "regex": None}
                    ]
                }
            },
            ValueError,
        ),
        (
            {
                "archive_document": {
                    "raw_line_pickers": [
                        {
                            "column_index": 0,
                            "pick_types": [
                                "first_number",
                            ],
                            "regex": None,
                        }
                    ]
                }
            },
            None,
        ),
        (
            {
                "archive_document": {
                    "raw_line_pickers": [
                        {
                            "column_index": 1,
                            "pick_types": [
                                "issue_type",
                                "issue_title",
                                "issue_location",
                                "issue_url",
                            ],
                            "regex": "\\((.*?)\\)(.*)\\[(.*?)\\]{1}\\(?(.+(?=\\)))?",
                        }
                    ]
                }
            },
            None,
        ),
    ],
)
def test_check_raw_line_picker(
    test_config: dict[str, Any], exception: type[Exception] | None
):
    if exception is None:
        check_raw_line_picker(test_config)
    else:
        with pytest.raises(exception):
            check_raw_line_picker(test_config)
