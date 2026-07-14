from pathlib import Path
from typing import Optional

import pytest

from mk_eda.libs.functions.boolean_matching import BooleanMatching

TEST_FILES_DIR = Path(__file__).parent / "data"


def read_file(filename: str) -> str:
    with open(filename) as file:
        return file.read().rstrip("\n")


@pytest.mark.parametrize(
    "file1_name, file2_name, expected",
    [
        (
            "test_matching_pair21.v",
            "test_matching_pair22.v",
            [
                (["~b = b", "c = ~c", "a = a"], "alpha", "g"),
                (["a = ~a", "c = b", "b = c"], "betta", "f"),
                (["a = ~a", "b = c", "c = b"], "gamma", "h"),
            ],
        ),
        (
            "test_matching_pair11.v",
            "test_matching_pair12.v",
            [],
        ),
    ],
)
def test_check_matching(file1_name: str, file2_name: str, expected: Optional[list[tuple[list[str], str, str]]]):
    bm = BooleanMatching()
    verilog_code1 = read_file(str(TEST_FILES_DIR / file1_name))
    verilog_code2 = read_file(str(TEST_FILES_DIR / file2_name))
    check = bm.check_matching(verilog_code1, verilog_code2)
    print(check)
    print(expected)
    assert check == expected
