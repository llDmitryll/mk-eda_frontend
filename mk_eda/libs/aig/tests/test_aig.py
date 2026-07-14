from __future__ import annotations

import tempfile

import pytest

from mk_eda.libs.aig.aig import AndInverterGraph
from mk_eda.libs.graph.graph import AndNode, Child, Nodes


@pytest.mark.parametrize(
    "file_name, inp, expected",
    [
        ("test_aig_1_d.json", "x5", ["x1", "x2", "x3", "x4", "x5"]),
        ("test_aig_2_g.json", "x4", ["x1", "x2", "x3", "x4"]),
    ],
)
def test_add_input(file_name: str, inp: str, expected: list[str]):
    """Tests adding an input"""
    aig = AndInverterGraph.from_json(f"tests/verification/{file_name}")
    aig.add_input(inp)
    assert aig.inputs == expected


@pytest.mark.parametrize(
    "file_name, inp, expected",
    [
        ("test_aig_1_d.json", "y", ["f", "y"]),
        ("test_aig_2_g.json", "z", ["f", "z"]),
    ],
)
def test_add_output(file_name: str, inp: str, expected: list[str]):
    aig = AndInverterGraph.from_json(f"tests/verification/{file_name}")
    aig.add_output(inp)
    assert aig.outputs == expected


@pytest.mark.parametrize(
    "file_name, inp, expected",
    [
        ("test_aig_1_d.json", "x1", ["x2", "x3", "x4"]),
        ("test_aig_2_g.json", "x3", ["x1", "x2"]),
    ],
)
def test_delete_input(file_name: str, inp: str, expected: list[str]):
    """Tests deleting an input"""
    aig = AndInverterGraph.from_json(f"tests/verification/{file_name}")
    aig.delete_input(inp)
    assert aig.inputs == expected


@pytest.mark.parametrize(
    "file_name, node, expected",
    [
        (
            "test_aig_1_d.json",
            AndNode("y1", True, "x2", False),
            {
                "y1": AndNode("x1", True, "x2", True),
                "y2": AndNode("y1", True, "x3", True),
                "f": AndNode("y2", True, "x4", True),
                "y3": AndNode("y1", True, "x2", False),
            },
        ),
        (
            "test_aig_2_g.json",
            AndNode("x1", True, "x2", False),
            {
                "y1": AndNode("x1", True, "x2", True),
                "f": AndNode("y1", True, "x3", True),
                "y2": AndNode("x1", True, "x2", False),
            },
        ),
    ],
)
def test_add_node(file_name: str, node: AndNode, expected: Nodes):
    """Tests adding a node"""
    aig = AndInverterGraph.from_json(f"tests/verification/{file_name}")
    aig.add_node(node)
    assert aig.nodes == expected


@pytest.mark.parametrize(
    "file_name, node, expected",
    [
        (
            "test_aig_1_d.json",
            "f",
            {
                "y1": AndNode("x1", True, "x2", True),
                "y2": AndNode("y1", True, "x3", True),
            },
        ),
        (
            "test_aig_1_g.json",
            "y2",
            {
                "y1": AndNode("x1", False, "x2", False),
                "f": AndNode("y2", True, "x4", True),
            },
        ),
    ],
)
def test_delete_node(file_name: str, node: str, expected: Nodes):
    """Tests deleting a node"""
    aig = AndInverterGraph.from_json(f"tests/verification/{file_name}")
    aig.delete_node(node)
    assert aig.nodes == expected


@pytest.mark.parametrize(
    "file_name, expected",
    [
        (
            "test_aig_1_d.json",
            {
                "inputs": ["x1", "x2", "x3", "x4"],
                "outputs": ["f"],
                "nodes": {
                    "y1": AndNode("x1", True, "x2", True),
                    "y2": AndNode("y1", True, "x3", True),
                    "f": AndNode("y2", True, "x4", True),
                },
            },
        ),
        (
            "test_aig_1_g.json",
            {
                "inputs": ["x1", "x2", "x3", "x4"],
                "outputs": ["f"],
                "nodes": {
                    "y1": AndNode("x1", False, "x2", False),
                    "y2": AndNode("y1", False, "x3", True),
                    "f": AndNode("y2", True, "x4", True),
                },
            },
        ),
    ],
)
def test_loading(file_name: str, expected: Nodes):
    """Tests json parsing and nodes loading"""
    aig = AndInverterGraph()
    aig.load(f"tests/verification/{file_name}")
    assert aig.inputs == expected["inputs"]
    assert aig.outputs == expected["outputs"]
    assert aig.nodes == expected["nodes"]


@pytest.mark.parametrize(
    "file_name",
    [
        "test_aig_1_d.json",
        "test_aig_2_g.json",
    ],
)
def test_dumping(file_name: str):
    """Tests json parsing and nodes loading"""
    aig = AndInverterGraph.from_json(f"tests/verification/{file_name}")
    with tempfile.NamedTemporaryFile() as out_file:
        aig.dump(out_file.name)
        check_aig = AndInverterGraph.from_json(out_file.name)
    assert check_aig.inputs == aig.inputs
    assert check_aig.outputs == aig.outputs
    assert check_aig.nodes == aig.nodes


@pytest.mark.parametrize(
    "file_name, expected",
    [
        (
            "test_aig_1_d.json",
            {
                "y1": AndNode("x1", True, "x2", True),
                "y2": AndNode("y1", True, "x3", True),
                "f": AndNode("y2", True, "x4", True),
                "y3": AndNode("y1", False, "y2", False),
                "y4": AndNode("y3", False, "1", True),
            },
        ),
        (
            "test_aig_1_g.json",
            {
                "y1": AndNode("x1", False, "x2", False),
                "y2": AndNode("y1", False, "x3", True),
                "f": AndNode("y2", True, "x4", True),
                "y3": AndNode("y1", False, "y2", False),
                "y4": AndNode("y3", False, "1", True),
            },
        ),
    ],
)
def test_nor(file_name: str, expected: Nodes):
    """Tests f_or function"""
    aig = AndInverterGraph.from_json(f"tests/verification/{file_name}")
    aig.f_or(Child("y1", True), Child("y2", True))
    assert aig.nodes == expected


@pytest.mark.parametrize(
    "file_name, expected",
    [
        (
            "test_aig_1_d.json",
            {
                "y1": AndNode("x1", True, "x2", True),
                "y2": AndNode("y1", True, "x3", True),
                "f": AndNode("y2", True, "x4", True),
                "y3": AndNode("y1", True, "y2", True),
                "y4": AndNode("x1", True, "f", True),
            },
        ),
        (
            "test_aig_1_g.json",
            {
                "y1": AndNode("x1", False, "x2", False),
                "y2": AndNode("y1", False, "x3", True),
                "f": AndNode("y2", True, "x4", True),
                "y3": AndNode("y1", True, "y2", True),
                "y4": AndNode("x1", True, "f", True),
            },
        ),
    ],
)
def test_and(file_name: str, expected: Nodes):
    """Tests f_or function"""
    aig = AndInverterGraph.from_json(f"tests/verification/{file_name}")
    aig.f_and(Child("y1", True), Child("y2", True))
    aig.f_and(Child("x1", True), Child("f", True))
    assert aig.nodes == expected


@pytest.mark.parametrize(
    "file_name, expected",
    [
        (
            "test_aig_1_d.json",
            {
                "y1": AndNode("x1", True, "x2", True),
                "y2": AndNode("y1", True, "x3", True),
                "f": AndNode("y2", True, "x4", True),
                "y3": AndNode("y1", True, "y2", False),
                "y4": AndNode("y1", False, "y2", True),
                "y5": AndNode("y3", False, "y4", False),
                "y6": AndNode("y5", False, "1", True),
            },
        ),
        (
            "test_aig_1_g.json",
            {
                "y1": AndNode("x1", False, "x2", False),
                "y2": AndNode("y1", False, "x3", True),
                "f": AndNode("y2", True, "x4", True),
                "y3": AndNode("y1", True, "y2", False),
                "y4": AndNode("y1", False, "y2", True),
                "y5": AndNode("y3", False, "y4", False),
                "y6": AndNode("y5", False, "1", True),
            },
        ),
    ],
)
def test_xor(file_name: str, expected: Nodes):
    """Tests f_xor function"""
    aig = AndInverterGraph.from_json(f"tests/verification/{file_name}")
    aig.f_xor(Child("y1", True), Child("y2", True))
    assert aig.nodes == expected


@pytest.mark.parametrize(
    "file_name, values, node, expected",
    [
        ("test_aig_1_d.json", {"x1": False, "x2": True, "x3": True, "x4": True}, "f", False),
        ("test_aig_1_d.json", {"x1": True, "x2": True, "x3": False, "x4": True}, "f", False),
        ("test_aig_1_d.json", {"x1": True, "x2": True, "x3": True, "x4": True}, "f", True),
        ("test_aig_1_d.json", {"x1": True, "x2": True, "x3": True, "x4": True}, "y4", True),
        ("test_aig_1_d.json", {"x1": False, "x2": False, "x3": False, "x4": True}, "y3", True),
        ("test_aig_1_d.json", {"x1": False, "x2": True, "x3": False, "x4": True}, "y4", False),
        ("test_aig_1_g.json", {"x1": True, "x2": True, "x3": False, "x4": True}, "x3", False),
        ("test_aig_1_g.json", {"x1": True, "x2": True, "x3": False, "x4": True}, "y8", False),
        ("test_aig_1_g.json", {"x1": False, "x2": True, "x3": True, "x4": True}, "y8", True),
        ("test_aig_1_g.json", {"x1": False, "x2": False, "x3": False, "x4": True}, "y4", True),
    ],
)
def test_evaluate(file_name: str, values: dict[str, bool], node: str, expected: bool):
    """Tests evaluating"""
    aig = AndInverterGraph.from_json(f"tests/verification/{file_name}")
    print(aig.f_or(Child("y1", True), Child("y2", True)))
    print(aig.f_xor(Child("x1", True), Child("x2", True)))
    assert aig.evaluate(node, values) == expected
