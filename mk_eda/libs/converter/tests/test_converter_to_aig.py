import json
from pathlib import Path

import pytest

from mk_eda.libs.converter.converter_to_aig import convert_binary_vectors_to_aig


@pytest.mark.parametrize(
    "file_name,expected_file",
    [
        ("./mk_eda/libs/converter/tests/data/test_01.txt", "./mk_eda/libs/converter/tests/data/test_01_expected.json"),
        ("./mk_eda/libs/converter/tests/data/test_02.txt", "./mk_eda/libs/converter/tests/data/test_02_expected.json"),
        ("./mk_eda/libs/converter/tests/data/test_03.txt", "./mk_eda/libs/converter/tests/data/test_03_expected.json"),
        ("./mk_eda/libs/converter/tests/data/test_04.txt", "./mk_eda/libs/converter/tests/data/test_04_expected.json"),
    ],
)
def test_convert_binary_vectors_to_aig(file_name: Path, expected_file: Path, tmp_path: Path):
    file_name = Path(file_name)
    expected_file = Path(expected_file)
    output_file: Path = tmp_path / "output.json"

    convert_binary_vectors_to_aig(file_name, output_file)

    with open(output_file) as file:
        result = json.load(file)

    with open(expected_file) as file:
        expected = json.load(file)

    assert result == expected
