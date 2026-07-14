import pytest

from mk_eda.libs.graph.graph import Child, Node
from mk_eda.libs.mig.mig import MajorityInverterGraph

directory = "mk_eda/libs/mig/tests/data/"


@pytest.mark.parametrize(
    "file_name, node, expected",
    [
        ("mig_1.json", ("y2", ("x1", 1, "x2", 1, "x3", 1)), "add_node_1.json"),
        ("mig_2.json", ("y4", ("y1", 1, "y2", 1, "y3", 1)), "add_node_2.json"),
    ],
)
def test_f_maj(file_name: str, node: tuple[str, tuple[str, int, str, int, str, int]], expected: str):
    mig = MajorityInverterGraph.from_json(directory + file_name)

    first = Child(node[1][0], node[1][1] == 1)
    second = Child(node[1][2], node[1][3] == 1)
    third = Child(node[1][4], node[1][5] == 1)
    mig.f_maj(first, second, third, node[0])

    result = MajorityInverterGraph.from_json(directory + expected)
    assert mig.inputs == result.inputs
    assert mig.outputs == result.outputs
    assert mig.nodes == result.nodes


@pytest.mark.parametrize(
    "file_name, root, expected", [("mig_2.json", "y2", "subgraph.json"), ("mig_2.json", "f", "full_graph.json")]
)
def test_subgraph(file_name: str, root: str, expected: str):
    mig = MajorityInverterGraph.from_json(directory + file_name)

    mig = mig.subgraph(root)

    result = MajorityInverterGraph.from_json(directory + expected)
    assert mig.inputs == result.inputs
    assert mig.outputs == result.outputs
    assert mig.nodes == result.nodes


def test_exceptions():
    mig = MajorityInverterGraph.from_json(directory + "mig_2.json")

    with pytest.raises(KeyError) as excinfo:
        first = Child("x1", True)
        second = Child("x2", False)
        third = Child("y100", False)
        mig.f_maj(first, second, third)
    assert "Invalid node wrong child y100" in str(excinfo.value)

    with pytest.raises(KeyError) as excinfo:
        node = Node("and", ["x1", 1, "x2", 1])
        mig.add_node(node)
    assert "Invalid vertex function 'and'" in str(excinfo.value)

    with pytest.raises(KeyError) as excinfo:
        mig.subgraph("y100")
    assert "Invalid node y100" in str(excinfo.value)

    with pytest.raises(KeyError) as excinfo:
        mig.load(directory + "wrong.json", True)
    assert "Invalid function set for MajorityInverterGraph" in str(excinfo.value)
