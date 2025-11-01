import os
import json
from pathlib import Path

from env import Env
from log import Log
from data_source import DataSource
from json_config import Config
from exception import ErrorMessage, ParseConfigError
from get_args import get_value_from_args, get_value_from_args_or_default
from config_checker import ConfigChecker

FORMAT_MAP_BLACK_LIST = [
    "version_regex",
    "introduced_version_reges",
    "archive_template",
]


def str_to_bool(s: str) -> bool:
    result = False
    result = s.lower() in ["true", "yes", "y", "1"]
    return result


class ArgsConfigDataSource(DataSource):
    def load(self, config: Config) -> None:
        try:
            config.config_path = get_value_from_args(
                "-c",
                "--config",
            )
        except ValueError:
            raise ValueError(Log.config_path_not_found)

        config.repository_token = get_value_from_args_or_default(
            "-t", "--repository-token"
        )
        config.version_start = get_value_from_args("-vs", "--version-start")
        config.version_end = get_value_from_args("-ve", "--version-end")
        config.ignore_introduce_version = str_to_bool(
            get_value_from_args_or_default("-iiv", "--ignore-introduce-version")
        )
        config.include_start_version = str_to_bool(
            get_value_from_args_or_default("-isv", "--include-start-version")
        )
        config.include_end_version = str_to_bool(
            get_value_from_args_or_default("-iev", "--include-end-version")
        )

        print(
            Log.input_version_range.format(
                start=config.version_start, end=config.version_end
            )
        )
        print(
            Log.ignore_introduce_version.format(
                ignore_introduce_version=config.ignore_introduce_version
            )
        )
        print(Log.include_start_version.format(result=config.include_start_version))
        print(Log.include_end_version.format(result=config.include_end_version))


class EnvConfigDataSource(DataSource):
    def load(self, config: Config) -> None:
        if config.repository_token == "":
            config.repository_token = os.environ.get(Env.REPOSITORY_TOKEN, "")
            if config.repository_token == "":
                print(Log.repository_token_not_found)


class JsonConfigDataSource(DataSource):
    def __init__(self, json_path: str):
        super().__init__()
        self.json_path = json_path

    def load(self, config: Config) -> None:
        config_path = self.json_path

        print(Log.loading_something.format(something=config_path))

        try:
            raw_json: dict = dict(
                json.loads(Path(config_path).read_text(encoding="utf-8"))
            )
            ConfigChecker.run_all(raw_json)

            raw_line_pickers = [
                Config.RawLinePicker(**dict_item)
                for dict_item in raw_json["archive_document"].pop("raw_line_pickers")
            ]
            archive_document = Config.ArchivedDocument(
                **raw_json.pop("archive_document")
            )
            archived_issues_info = [
                Config.ArchivedIssuesInfo(**dict_item)
                for dict_item in raw_json.pop("archived_issues_info")
            ]
            print(Log.load_archived_source.format(count=len(archived_issues_info)))
            config.__dict__.update(**raw_json)
            config.archive_document = archive_document
            config.archive_document.raw_line_pickers = raw_line_pickers
            config.archived_issues_info = archived_issues_info
        except Exception as exc:
            raise ParseConfigError(ErrorMessage.parse_config_failed.format(exc=exc))

        print(Log.loading_something_success.format(something=config_path))
