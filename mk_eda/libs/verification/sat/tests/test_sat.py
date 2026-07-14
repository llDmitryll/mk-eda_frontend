import os

import pytest
from pyeda.boolalg.expr import And, Expression, exprvar  # type: ignore

from mk_eda.libs.common.constants import PROJECT_DIR
from mk_eda.libs.graph.graph import Ports, RawNodes, nodes_to_raw
from mk_eda.libs.verification.sat.sat import Sat


@pytest.mark.parametrize(
    "json_file, expected_inputs, expected_outputs, expected_nodes",
    [
        (
            "test_aig_1_d.json",
            ["x1", "x2", "x3", "x4"],
            ["f"],
            {"y1": ["and", "x1", 1, "x2", 1], "y2": ["and", "y1", 1, "x3", 1], "f": ["and", "y2", 1, "x4", 1]},
        ),
        (
            "test_aig_1_g.json",
            ["x1", "x2", "x3", "x4"],
            ["f"],
            {"y1": ["and", "x1", 0, "x2", 0], "y2": ["and", "y1", 0, "x3", 1], "f": ["and", "y2", 1, "x4", 1]},
        ),
        (
            "test_aig_2_d.json",
            ["x1", "x2", "x3"],
            ["f"],
            {"y1": ["and", "x1", 0, "x2", 1], "f": ["and", "y1", 1, "x3", 0]},
        ),
        (
            "test_aig_2_g.json",
            ["x1", "x2", "x3"],
            ["f"],
            {"y1": ["and", "x1", 1, "x2", 1], "f": ["and", "y1", 1, "x3", 1]},
        ),
    ],
)
def test_parse_json(json_file: str, expected_inputs: Ports, expected_outputs: Ports, expected_nodes: RawNodes):
    """Test parsing json files"""
    file_path = os.path.join(PROJECT_DIR, "tests/verification", json_file)
    circuit = Sat.from_json(file_path)
    assert circuit.inputs == expected_inputs
    assert circuit.outputs == expected_outputs
    assert nodes_to_raw(circuit.nodes) == expected_nodes


@pytest.mark.parametrize(
    "json_file, expected_formula",
    [
        (
            "test_aig_1_d.json",
            And(exprvar("x1"), exprvar("x2"), exprvar("x3"), exprvar("x4")),  # type: ignore
        ),
        (
            "test_aig_1_g.json",
            And(~(And(~exprvar("x1"), ~exprvar("x2"))), exprvar("x3"), exprvar("x4")),  # type: ignore
        ),
        (
            "test_aig_2_d.json",
            And(~exprvar("x1"), exprvar("x2"), ~exprvar("x3")),  # type: ignore
        ),
        (
            "test_aig_2_g.json",
            And(exprvar("x1"), exprvar("x2"), exprvar("x3")),  # type: ignore
        ),
    ],
)
def test_construct_output_formula(json_file: str, expected_formula: Expression):
    """Test constructing output formulas."""
    json_file = os.path.join(PROJECT_DIR, "tests/verification", json_file)
    circuit = Sat.from_json(json_file)

    for output in circuit.outputs:
        assert circuit[output].equivalent(expected_formula)  # type: ignore


@pytest.mark.parametrize(
    "json_file1, json_file2, expected_result",
    [
        ("test_aig_1_d.json", "test_aig_1_g.json", True),
        ("test_aig_2_d.json", "test_aig_2_g.json", True),
        ("test_aig_1_d.json", "test_aig_2_d.json", True),
        ("test_aig_1_g.json", "test_aig_2_g.json", True),
        ("test_aig_1_d.json", "test_aig_1_d.json", False),
        ("test_equ_1_d.json", "test_equ_1_g.json", False),
    ],
)
def test_find_unequal_set(json_file1: str, json_file2: str, expected_result: bool):
    """Test checking equivalence of circuits."""
    file_path1 = os.path.join(PROJECT_DIR, "tests/verification", json_file1)
    file_path2 = os.path.join(PROJECT_DIR, "tests/verification", json_file2)

    circuit1 = Sat.from_json(file_path1)
    circuit2 = Sat.from_json(file_path2)

    for output in circuit1.outputs:
        unequal_set = Sat.find_unequal_set(circuit1[output], circuit2[output])
        assert bool(unequal_set) == expected_result

        if unequal_set:
            f1 = circuit1[output].restrict(unequal_set)  # type: ignore
            f2 = circuit2[output].restrict(unequal_set)  # type: ignore
            assert not f1.equivalent(f2)  # type: ignore
