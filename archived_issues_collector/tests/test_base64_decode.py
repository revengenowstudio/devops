import pytest

from src.base64_decode import base64_decode_str


@pytest.mark.parametrize(
    "data,expected",
    [
        ("aGVsbG8sd29ybGQgCuS9oOWlveS4lueVjCANCg==", "hello,world \n你好世界 \r\n"),
    ],
)
def test_base64_decode_str(data: str, expected: str):
    assert base64_decode_str(data) == expected
