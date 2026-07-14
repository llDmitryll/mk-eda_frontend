from typing import Union

import pytest

from mk_eda.libs.graph.graph import Child, Node
from mk_eda.libs.xaig.xaig import XorAndInverterGraph

directory = "mk_eda/libs/xaig/tests/data/"


@pytest.mark.parametrize(
    "file_name, node, expected",
    [
        ("right.json", ["y4", ("x1", 1, "x3", 0)], "and_inputs.json"),
        ("right.json", ["y4", ("y1", 1, "y2", 0)], "and_nodes.json"),
    ],
)
def test_f_and(file_name: str, node: list[Union[str, tuple[str, int, str, int]]], expected: str):
    xaig = XorAndInverterGraph.from_json(directory + file_name)

    left = Child(node[1][0], node[1][1] == 1)
    right = Child(node[1][2], node[1][3] == 1)

    xaig.f_and(left, right, str(node[0]))

    result = XorAndInverterGraph.from_json(directory + expected)
    assert xaig.inputs == result.inputs
    assert xaig.outputs == result.outputs
    assert xaig.nodes == result.nodes


@pytest.mark.parametrize(
    "file_name, node, expected",
    [
        ("right.json", ["y4", ("x1", 1, "x3", 0)], "xor_inputs.json"),
        ("right.json", ["y4", ("y1", 1, "y2", 1)], "xor_nodes.json"),
    ],
)
def test_f_xor(file_name: str, node: list[Union[str, tuple[str, int, str, int]]], expected: str):
    xaig = XorAndInverterGraph.from_json(directory + file_name)

    left = Child(node[1][0], node[1][1] == 1)
    right = Child(node[1][2], node[1][3] == 1)

    xaig.f_xor(left, right, str(node[0]))

    result = XorAndInverterGraph.from_json(directory + expected)
    assert xaig.inputs == result.inputs
    assert xaig.outputs == result.outputs
    assert xaig.nodes == result.nodes


def test_exceptins():
    xaig = XorAndInverterGraph.from_json(directory + "right.json")

    with pytest.raises(KeyError) as excinfo:
        left = Child("x1", True)
        right = Child("y100", False)
        xaig.f_and(left, right)
    assert "Invalid node y100" in str(excinfo.value)

    with pytest.raises(KeyError) as excinfo:
        left = Child("x1", True)
        right = Child("y100", False)
        xaig.f_xor(left, right)
    assert "Invalid node y100" in str(excinfo.value)

    with pytest.raises(KeyError) as excinfo:
        node = Node("or", ["x1", 1, "x2", 1])
        xaig.add_node(node)
    assert "Invalid vertex function 'or'" in str(excinfo.value)

    with pytest.raises(KeyError) as excinfo:
        xaig.load(directory + "wrong.json", True)
    assert "Invalid function set for XorAndInverterGraph" in str(excinfo.value)
