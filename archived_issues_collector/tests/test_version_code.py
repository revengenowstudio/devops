import pytest

from src.version_code import VersionCode


class TestVersionCode:

    @pytest.mark.parametrize("input,expected", [
        ("0.99.919", None),
        ("0.99.919a", None),
        ("0.99.919a33", None),
        ("G1024", None),
        ("G1024P", None),
        ("G1024P3", None),
        ("原版yr", 0),
        ("未知", 0),
    ])
    def test_to_int64(self, input: str, expected: int | None):
        if expected is None:
            VersionCode(input).to_int64()
            return
        assert VersionCode(input).to_int64() == expected

    def test_version_compare(
            self,

    ):
        # 请保证列表的元素顺序是按版本号从小到大升序排列
        # 元素的顺序决定了断言的预期值
        new_version_list = ['0.99.914b2', '0.99.914b55',
                            '0.99.916', '0.99.916',
                            '0.99.917', '0.99.917',
                            '0.99.918b2', '0.99.918',
                            '0.99.919a33', '0.99.919b36',
                            '0.99.919b55', '0.99.919', ]
        old_version_list = ["E907", "F0930",
                            "F1024", "G1208",
                            "G1208P", "G1208P3",
                            ]
        special_version_list = ["原版yr", "原版YR", "未知"]
        operators = [">", "<", ">=", "<=", "==", "!="]

        # new_version_list.sort()
        # old_version_list.sort()

        sorted_version_list = [
            *old_version_list,
            *new_version_list
        ]

        def compare_version(left: VersionCode, right: VersionCode,
                            operator: str, expected: bool) -> None:
            match operator:
                case ">":
                    assert (left > right) is expected
                case ">=":
                    assert (left >= right) is expected
                case "<":
                    assert (left < right) is expected
                case "<=":
                    assert (left <= right) is expected
                case "==":
                    assert (left == right) is expected
                case "!=":
                    assert (left != right) is expected

        for left_str in sorted_version_list:
            left = VersionCode(left_str)
            for right_str in sorted_version_list:
                right = VersionCode(right_str)
                for operator in operators:
                    expected = eval(
                        "{left_index} {operator} {right_index}".
                        format(
                            left_index=sorted_version_list.index(left_str),
                            right_index=sorted_version_list.index(right_str),
                            operator=operator
                        )
                    )
                    compare_version(
                        left, right, operator, expected
                    )

        for left_str in special_version_list:
            left = VersionCode(left_str)
            for right_str in sorted_version_list:
                right = VersionCode(right_str)
                for operator in operators:
                    expected = False
                    if (operator == "<"
                        or operator == "<="
                            or operator == "!="):
                        expected = True

                    compare_version(
                        left, right, operator, expected
                    )

    @pytest.mark.parametrize(
        "min_version_str,input_version_list,max_version_str,expected",
        [
            ("0.99.914b3",
             ["0.99.914b3", "0.99.914c1",
              "0.99.915c3", "0.99.915c5"],
             "0.99.915c5", True),
            ("0.99.914p3",
             ["原版YR", "G1024", "G1024P3",
              "0.99.913", "0.99.916"],
             "0.99.915c3", False),
            ("0.99.915",
             ["原版YR", "G1024", "G1024P3",
              "0.99.915a1", "0.99.915b2",
              "0.99.917"
              ],
             "0.99.916", False),
            ("0.99.915",
             ["0.99.915", "0.99.916",
              "0.99.916a1", "0.99.916b3"],
             "0.99.916", True),
            ("G1024B1",
             ["G1024B1", "G1024B3", "G1124", "G1124H5",
              "H0102", "H0102P5"],
             "H0102P5", True),
            ("G1024B1",
             ["原版YR", "E907", "E0907", "G1024",
              "H0102P7", "H0520", "0.99.916"],
             "H0102P5", False),
        ])
    def test_range_version_compare(
        self,
        min_version_str: str,
        input_version_list: list[str],
        max_version_str: str,
        expected: bool,
    ):

        min_version = VersionCode(min_version_str)
        max_version = VersionCode(max_version_str)
        for input_str in input_version_list:
            input_version = VersionCode(input_str)
            assert (min_version <= input_version <= max_version) == expected
