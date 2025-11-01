import json

import pytest

from src.json_dumps import json_dumps


@pytest.mark.parametrize(
    "test_dict",
    [
        {"a": 1, "b": 2},
        {"issue_id": 1, "issue_type": "设定调整"},
    ],
)
def test_json_dumps(test_dict: dict):
    assert json_dumps(test_dict) == json.dumps(test_dict, indent=4, ensure_ascii=False)
    assert json_dumps(test_dict, indent=2) == json.dumps(
        test_dict, indent=2, ensure_ascii=False
    )
