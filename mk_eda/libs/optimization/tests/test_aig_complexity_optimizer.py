import os

import pytest

from mk_eda.libs.aig.aig import AndInverterGraph
from mk_eda.libs.optimization.aig_complexity_optimizer import AIGComplexityOptimizer

base_path = "./mk_eda/libs/optimization/tests/aig_complexity_data/"
test_cases = [(f"test_{i}.json", f"test_{i}_expected.json") for i in range(1, 10)]


@pytest.mark.parametrize(
    "input_file,expected_file",
    [
        (os.path.join(base_path, input_file), os.path.join(base_path, expected_file))
        for input_file, expected_file in test_cases
    ],
)
def test_aig_complexity_optimizer(input_file: str, expected_file: str):
    optimizer = AIGComplexityOptimizer()
    aig = AndInverterGraph.from_json(input_file)
    expected_aig = AndInverterGraph.from_json(expected_file)
    optimized_aig = optimizer(aig)

    assert optimized_aig.inputs == expected_aig.inputs
    assert optimized_aig.outputs == expected_aig.outputs
    assert optimized_aig.nodes == expected_aig.nodes
