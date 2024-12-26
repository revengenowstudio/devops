from unittest.mock import patch

import pytest

from src.get_args import (get_value_from_args,
                          get_value_from_args_or_default)


@pytest.mark.parametrize(
    "short_arg,long_arg,value", [
        ("-o", "--open", "这是中文"),
        ("-O", "--OPEN", "this is value"),

    ])
def test_get_value_from_args(
    short_arg: str,
    long_arg: str,
    value: str
):
    with patch("sys.argv", [short_arg, value]):
        assert get_value_from_args(short_arg, long_arg) == value
    with patch("sys.argv", [long_arg, value]):
        assert get_value_from_args(short_arg, long_arg) == value
    with pytest.raises(ValueError):
        get_value_from_args(short_arg, long_arg)
        
@pytest.mark.parametrize(
    "short_arg,long_arg,value", [
        ("-o", "--open", "这是中文"),
        ("-O", "--OPEN", "this is value"),

    ])
def test_get_value_from_args_or_default(
    short_arg: str,
    long_arg: str,
    value: str
):
    with patch("sys.argv", [short_arg, value]):
        assert get_value_from_args_or_default(short_arg, long_arg) == value
    with patch("sys.argv", [long_arg, value]):
        assert get_value_from_args_or_default(short_arg, long_arg) == value
    assert get_value_from_args_or_default(short_arg, long_arg) == ""
