from typing import Any, Callable

from exception import ErrorMessage
from json_dumps import json_dumps


class ConfigChecker():
    _registered_functions = []

    @staticmethod
    def register(func: Callable[[dict[str, str]], None]):
        ConfigChecker._registered_functions.append(func)
        return func

    @staticmethod
    def run_all(raw_config: dict[str, str]) -> None:
        for func in ConfigChecker._registered_functions:
            func(raw_config)


@ConfigChecker.register
def check_raw_line_picker(raw_config: dict[str, Any]) -> None:
    raw_line_pickers: list[dict[str, str]] = raw_config[
        "archive_document"]["raw_line_pickers"]
    for picker in raw_line_pickers:
        if (picker["regex"] is None
                and len(picker["pick_types"]) > 1):
            raise ValueError(
                ErrorMessage.too_mach_pick_types
                .format(
                    picker_type=picker["pick_types"]
                ))
        if len(picker["pick_types"]) == 0:
            raise ValueError(
                ErrorMessage.pick_types_is_empty
                .format(
                    picker=json_dumps(picker)
                ))
