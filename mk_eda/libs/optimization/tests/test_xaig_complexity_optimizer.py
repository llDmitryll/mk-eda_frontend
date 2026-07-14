import json
from pathlib import Path

import pytest

from mk_eda.libs.optimization.xaig_complexity_optimizer import XAIGComplexityOptimizer
from mk_eda.libs.xaig.xaig import XorAndInverterGraph


@pytest.mark.parametrize(
    "input_file,expected_file",
    [
        (
            "./mk_eda/libs/optimization/tests/xaig_complexity_data/test_01.json",
            "./mk_eda/libs/optimization/tests/xaig_complexity_data/test_01_expected.json",
        ),
        (
            "./mk_eda/libs/optimization/tests/xaig_complexity_data/test_02.json",
            "./mk_eda/libs/optimization/tests/xaig_complexity_data/test_02_expected.json",
        ),
        (
            "./mk_eda/libs/optimization/tests/xaig_complexity_data/test_03.json",
            "./mk_eda/libs/optimization/tests/xaig_complexity_data/test_03_expected.json",
        ),
    ],
)
def test_xaig_complexity_optimizer(input_file: str, expected_file: str, tmp_path: Path):
    output_file: Path = tmp_path / "output.json"

    xaig = XorAndInverterGraph.from_json(input_file)
    xaig_opt = XAIGComplexityOptimizer()

    xaig = xaig_opt(xaig)

    xaig.dump(str(output_file))

    with open(output_file) as file:
        result = json.load(file)

    with open(expected_file) as file:
        expected = json.load(file)

    assert result == expected
