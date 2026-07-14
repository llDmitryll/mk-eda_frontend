from pathlib import Path
from typing import Union

import pytest

from mk_eda.libs.graph.graph import Child, MajorityNode, Nodes, XorNode
from mk_eda.libs.xmig.xmig import XorMajorityInverterGraph


@pytest.mark.parametrize(
    "file_name, inp, expected",
    [
        ("./mk_eda/libs/xmig/tests/data/test_01.json", "x4", ["x1", "x2", "x3", "x4"]),
        ("./mk_eda/libs/xmig/tests/data/test_02.json", "x5", ["x1", "x2", "x3", "x4", "x5"]),
    ],
)
def test_add_input(file_name: str, inp: str, expected: list[str]):
    """Tests adding an input"""
    xmig = XorMajorityInverterGraph.from_json(file_name)
    xmig.add_input(inp)
    assert xmig.inputs == expected


@pytest.mark.parametrize(
    "file_name, inp, expected",
    [
        ("./mk_eda/libs/xmig/tests/data/test_01.json", "y", ["f", "y"]),
        ("./mk_eda/libs/xmig/tests/data/test_02.json", "z", ["f", "z"]),
    ],
)
def test_add_output(file_name: str, inp: str, expected: list[str]):
    xmig = XorMajorityInverterGraph.from_json(file_name)
    xmig.add_output(inp)
    assert xmig.outputs == expected


@pytest.mark.parametrize(
    "file_name, inp, expected",
    [
        ("./mk_eda/libs/xmig/tests/data/test_01.json", "x1", ["x2", "x3"]),
        ("./mk_eda/libs/xmig/tests/data/test_02.json", "x3", ["x1", "x2", "x4"]),
    ],
)
def test_delete_input(file_name: str, inp: str, expected: list[str]):
    """Tests deleting an input"""
    xmig = XorMajorityInverterGraph.from_json(file_name)
    xmig.delete_input(inp)
    assert xmig.inputs == expected


@pytest.mark.parametrize(
    "file_name, node, expected",
    [
        (
            "./mk_eda/libs/xmig/tests/data/test_03.json",
            XorNode("y1", True, "x2", False),
            {
                "y1": XorNode("x1", True, "x2", True),
                "y2": XorNode("y1", True, "x3", True),
                "f": XorNode("y2", True, "x4", True),
                "y3": XorNode("y1", True, "x2", False),
            },
        ),
        (
            "./mk_eda/libs/xmig/tests/data/test_04.json",
            XorNode("x1", True, "x2", False),
            {
                "y1": XorNode("x1", True, "x2", True),
                "f": XorNode("y1", True, "x3", True),
                "y2": XorNode("x1", True, "x2", False),
            },
        ),
    ],
)
def test_add_node(file_name: str, node: XorNode, expected: Nodes):
    """Tests adding a node"""
    xmig = XorMajorityInverterGraph.from_json(file_name)
    xmig.add_node(node)
    assert xmig.nodes == expected


@pytest.mark.parametrize(
    "file_name, node, expected",
    [
        (
            "./mk_eda/libs/xmig/tests/data/test_03.json",
            "f",
            {
                "y1": XorNode("x1", True, "x2", True),
                "y2": XorNode("y1", True, "x3", True),
            },
        ),
        (
            "./mk_eda/libs/xmig/tests/data/test_05.json",
            "y2",
            {
                "y1": XorNode("x1", True, "x2", True),
                "f": XorNode("y1", True, "y2", True),
            },
        ),
    ],
)
def test_delete_node(file_name: str, node: str, expected: Nodes):
    """Tests deleting a node"""
    xmig = XorMajorityInverterGraph.from_json(file_name)
    xmig.delete_node(node)
    assert xmig.nodes == expected


@pytest.mark.parametrize(
    "file_name, expected",
    [
        (
            "./mk_eda/libs/xmig/tests/data/test_01.json",
            {
                "inputs": ["x1", "x2", "x3"],
                "outputs": ["f"],
                "nodes": {
                    "y1": XorNode("x2", True, "x3", True),
                    "y2": XorNode("y1", True, "x1", True),
                    "f": MajorityNode("y1", True, "y2", True, "x2", True),
                },
            },
        ),
        (
            "./mk_eda/libs/xmig/tests/data/test_02.json",
            {
                "inputs": ["x1", "x2", "x3", "x4"],
                "outputs": ["f"],
                "nodes": {
                    "y1": XorNode("x1", True, "x2", False),
                    "y2": MajorityNode("y1", False, "x3", True, "x4", True),
                    "f": MajorityNode("y1", True, "y2", True, "x4", True),
                },
            },
        ),
    ],
)
def test_loading(file_name: str, expected: Nodes):
    """Tests json parsing and nodes loading"""
    xmig = XorMajorityInverterGraph()
    xmig.load(file_name)
    assert xmig.inputs == expected["inputs"]
    assert xmig.outputs == expected["outputs"]
    assert xmig.nodes == expected["nodes"]


@pytest.mark.parametrize(
    "file_name",
    [
        "./mk_eda/libs/xmig/tests/data/test_01.json",
        "./mk_eda/libs/xmig/tests/data/test_02.json",
    ],
)
def test_dumping(file_name: str, tmp_path: Path):
    """Tests json parsing and nodes loading"""
    output_file: Path = tmp_path / "output.json"
    xmig = XorMajorityInverterGraph.from_json(file_name)
    xmig.dump(str(output_file))
    check_xmg = XorMajorityInverterGraph.from_json(str(output_file))
    assert check_xmg.inputs == xmig.inputs
    assert check_xmg.outputs == xmig.outputs
    assert check_xmg.nodes == xmig.nodes


@pytest.mark.parametrize(
    "file_name, node, expected",
    [
        (
            "./mk_eda/libs/xmig/tests/data/test_01.json",
            ["y3", ("y1", 0, "y2", 0)],
            {
                "y1": XorNode("x2", True, "x3", True),
                "y2": XorNode("y1", True, "x1", True),
                "f": MajorityNode("y1", True, "y2", True, "x2", True),
                "y3": XorNode("y1", False, "y2", False),
            },
        ),
        (
            "./mk_eda/libs/xmig/tests/data/test_02.json",
            ["y3", ("y1", 1, "x4", 0)],
            {
                "y1": XorNode("x1", True, "x2", False),
                "y2": MajorityNode("y1", False, "x3", True, "x4", True),
                "f": MajorityNode("y1", True, "y2", True, "x4", True),
                "y3": XorNode("y1", True, "x4", False),
            },
        ),
    ],
)
def test_xor(file_name: str, node: list[Union[str, tuple[str, int, str, int]]], expected: Nodes):
    """Tests f_xor function"""
    aig = XorMajorityInverterGraph.from_json(file_name)
    left = Child(node[1][0], node[1][1] == 1)
    right = Child(node[1][2], node[1][3] == 1)
    aig.f_xor(left, right)
    assert aig.nodes == expected


@pytest.mark.parametrize(
    "file_name, node, expected",
    [
        (
            "./mk_eda/libs/xmig/tests/data/test_01.json",
            ["y3", ("y1", 0, "y2", 0, "x1", 1)],
            {
                "y1": XorNode("x2", True, "x3", True),
                "y2": XorNode("y1", True, "x1", True),
                "f": MajorityNode("y1", True, "y2", True, "x2", True),
                "y3": MajorityNode("y1", False, "y2", False, "x1", True),
            },
        ),
        (
            "./mk_eda/libs/xmig/tests/data/test_02.json",
            ["y3", ("y1", 1, "x3", 0, "x4", 1)],
            {
                "y1": XorNode("x1", True, "x2", False),
                "y2": MajorityNode("y1", False, "x3", True, "x4", True),
                "f": MajorityNode("y1", True, "y2", True, "x4", True),
                "y3": MajorityNode("y1", True, "x3", False, "x4", True),
            },
        ),
    ],
)
def test_majority(file_name: str, node: list[Union[str, tuple[str, int, str, int, str, int]]], expected: Nodes):
    """Tests f_or function"""
    aig = XorMajorityInverterGraph.from_json(file_name)
    first = Child(node[1][0], node[1][1] == 1)
    second = Child(node[1][2], node[1][3] == 1)
    third = Child(node[1][4], node[1][5] == 1)
    aig.f_majority(first, second, third)
    assert aig.nodes == expected


@pytest.mark.parametrize(
    "file_name, expected",
    [
        (
            "./mk_eda/libs/xmig/tests/data/test_01.json",
            {"total_nodes": 3, "xor_nodes": 2, "majority_nodes": 1},
        ),
        (
            "./mk_eda/libs/xmig/tests/data/test_02.json",
            {"total_nodes": 3, "xor_nodes": 1, "majority_nodes": 2},
        ),
        (
            "./mk_eda/libs/xmig/tests/data/test_03.json",
            {"total_nodes": 3, "xor_nodes": 3, "majority_nodes": 0},
        ),
        (
            "./mk_eda/libs/xmig/tests/data/test_04.json",
            {"total_nodes": 2, "xor_nodes": 2, "majority_nodes": 0},
        ),
        (
            "./mk_eda/libs/xmig/tests/data/test_05.json",
            {"total_nodes": 3, "xor_nodes": 2, "majority_nodes": 1},
        ),
    ],
)
def test_graph_statistics(file_name: str, expected: dict[str, int]):
    """Tests the graph statistics function"""
    xmig = XorMajorityInverterGraph.from_json(file_name)
    stats = xmig.graph_statistics()
    assert stats == expected
