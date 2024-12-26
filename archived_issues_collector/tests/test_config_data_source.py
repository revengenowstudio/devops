import os
import json
from pathlib import Path
from typing import Any
from unittest.mock import patch, MagicMock
from dataclasses import asdict

import pytest

from src.env import Env
from src.log import Log
from src.json_config import Config
from src.config_data_source import (
    JsonConfigDataSource,
    ArgsConfigDataSource,
    EnvConfigDataSource,
    str_to_bool
)


@pytest.mark.parametrize(
    "data,expected",
    [
        ("true", True), ("TRUE", True),
        ("yes", True), ("YES", True),
        ("y", True), ("Y", True),
        ("1", True),
        ("false", False), ("FALSE", False),
        ("no", False), ("NO", False),
        ("n", False), ("N", False),
        ("0", False),
    ]
)
def test_str_to_bool(data: str, expected: bool):
    assert str_to_bool(data) == expected


class TestArgsConfigDataSource():

    @pytest.mark.parametrize(
        "args,config_key,expected_value,exception",
        [
            ([], [], [], ValueError),
            (["--config", "test.json"], [], [], ValueError),
            (["--config", "test.json", "--version-start", "0.99.918"],
             [], [], ValueError),
            ([
                "--config", "test.json",
                "--repository-token", "test_token",
                "--version-start", "0.99.918",
                "--version-end", "0.99.919",
                "--match-introduce-version", "true"
            ],
                ["config_path", "repository_token", "version_start",
                 "version_end", "match_introduce_version"],
                ["test.json", "test_token", "0.99.918",
                 "0.99.919", True],
                None),
        ]
    )
    def test_load(
        self,
        args: list[str],
        config_key: list[str],
        expected_value: list[Any],
        exception: type[Exception] | None
    ):
        mock_config = Config()
        with patch("sys.argv", args):
            if exception is not None:
                with pytest.raises(
                        exception):
                    ArgsConfigDataSource().load(mock_config)
            else:
                ArgsConfigDataSource().load(mock_config)
                for key, value in zip(config_key, expected_value):
                    assert mock_config.__dict__[key] == value


class TestEnvConfigDataSource():

    @pytest.mark.parametrize(
        "args,config_key,expected_value,exception",
        [
            ({Env.REPOSITORY_TOKEN: "test_token_env"},
             ["repository_token"], ["test_token_env"], None),
        ]
    )
    def test_load(
        self,
        args: list[str],
        config_key: list[str],
        expected_value: list[Any],
        exception: type[Exception] | None
    ):
        mock_config = Config()
        with patch.dict(os.environ, args):
            if exception is not None:
                with pytest.raises(
                        exception):
                    EnvConfigDataSource().load(mock_config)
            else:
                mock_config.repository_token = "test_token"
                EnvConfigDataSource().load(mock_config)
                assert mock_config.repository_token == "test_token"

                mock_config.repository_token = ""
                EnvConfigDataSource().load(mock_config)
                for key, value in zip(config_key, expected_value):
                    assert mock_config.__dict__[key] == value


class TestJsonConfigDataSource():

    @pytest.mark.parametrize(
        "test_json_str",
        [
            '''{"archived_issues_info": [{"url": "https://example.com.md","json_api": false,"content_key": "content","base64_decode": false,"use_token": false,"http_headers": {"Accept": "application/vnd.github.raw+json"}}],"archive_document": {"skip_header_rows": 5,"table_separator": "|","reformat_template": "1. [{issue_type}({md_link_square_start}{issue_location}{md_link_square_end}{issue_url_parents})]  {issue_title}","raw_line_pickers": [{"column_index": 0,"pick_types": ["first_number"],"regex": null},{"column_index": 1,"pick_types": ["issue_type", "issue_title", "issue_location", "issue_url"],"regex": "\\\\((.*?)\\\\)(.*)\\\\[(.*?)\\\\]{1}\\\\(?(.+(?=\\\\)))?"},{"column_index": 2,"pick_types": ["introduce_version"],"regex": null},{"column_index": 3,"pick_types": ["archived_version"],"regex": null}]},"output_path": "./output/ChangeLog.md"}
            ''',
        ]
    )
    @patch("src.config_checker.ConfigChecker.run_all")
    def test_load(
        self,
        mock_run_all: MagicMock,
        test_json_str: str,
        tmp_path: str,
    ):
        tmp_dir = Path(tmp_path)
        tmp_dir.mkdir(exist_ok=True)
        tmp_file = Path(tmp_dir / "test.json")
        tmp_file.write_text(test_json_str, encoding="utf-8")

        mock_config = Config()
        mock_run_all.return_value = None

        JsonConfigDataSource(str(tmp_file)).load(mock_config)

        result_dict = asdict(mock_config)
        excepted_dict = json.loads(test_json_str)
        for key, _ in zip(excepted_dict.keys(), result_dict.keys()):
            assert result_dict[key] == excepted_dict[key]
