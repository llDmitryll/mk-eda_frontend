import pytest
from pyeda.boolalg.expr import exprvar  # type: ignore

from mk_eda.libs.graph.graph import BooleanFunction, InverterGraph, Node, Ports, RawNodes, nodes_from_raw


@pytest.mark.parametrize(
    "input_file, inputs, outputs, nodes",
    [
        (
            "test_aig_1_d.json",
            ["x1", "x2", "x3", "x4"],
            ["f"],
            {"y1": ["and", "x1", 1, "x2", 1], "y2": ["and", "y1", 1, "x3", 1], "f": ["and", "y2", 1, "x4", 1]},
        ),
        (
            "test_aig_2_d.json",
            ["x1", "x2", "x3"],
            ["f"],
            {"y1": ["and", "x1", 0, "x2", 1], "f": ["and", "y1", 1, "x3", 0]},
        ),
    ],
)
def test_load(input_file: str, inputs: Ports, outputs: Ports, nodes: RawNodes):
    """Tests load function"""
    circuit = InverterGraph()
    circuit.load(f"tests/verification/{input_file}")
    assert circuit.inputs == inputs
    assert circuit.outputs == outputs
    assert circuit.nodes == nodes_from_raw(nodes)


@pytest.mark.parametrize(
    "input_file, useful, cut, inputs, outputs, nodes, unaffected",
    [
        (
            "test_aig_1_d.json",
            7,
            ["y1"],
            ["x1", "x2", "x3", "x4", "y1"],
            ["f", "y3"],
            {"y2": ["and", "y1", 1, "x3", 1], "f": ["and", "y2", 1, "x4", 1], "y3": ["and", "x1", 1, "x2", 1]},
            5,
        ),
        (
            "test_aig_2_d.json",
            5,
            ["y1"],
            ["x1", "x2", "x3", "y1"],
            ["f", "y2"],
            {"f": ["and", "y1", 1, "x3", 0], "y2": ["and", "x1", 0, "x2", 1]},
            4,
        ),
    ],
)
def test_cut(
    input_file: str, useful: int, cut: list[str], inputs: Ports, outputs: Ports, nodes: RawNodes, unaffected: int
):
    """Tests cut function"""
    circuit = InverterGraph.from_json(f"tests/verification/{input_file}")
    for output in circuit.outputs:
        _ = circuit[output]
    assert len(circuit._cache) == useful  # type: ignore

    circuit.cut(cut)
    assert circuit.inputs == inputs
    assert circuit.outputs == outputs
    assert circuit.nodes == nodes_from_raw(nodes)
    assert len(circuit._cache) == unaffected  # type: ignore


@pytest.mark.parametrize(
    "input_file1, check_outputs1, input_file2, check_outputs2",
    [
        ("test_aig_3_d.json", ["y5", "f"], "test_aig_3_g.json", ["y3", "f"]),
        ("test_xor_1_d.json", ["y5", "f"], "test_xor_1_g.json", ["y3", "f"]),
        ("test_or_1_d.json", ["y5", "f"], "test_or_1_g.json", ["y3", "f"]),
        ("test_equ_2_d.json", ["f"], "test_equ_2_g.json", ["f"]),
    ],
)
def test_equal(input_file1: str, check_outputs1: list[str], input_file2: str, check_outputs2: list[str]):
    """Tests equivalence"""
    circuit1 = InverterGraph.from_json(f"tests/verification/{input_file1}")
    circuit2 = InverterGraph.from_json(f"tests/verification/{input_file2}")
    for f1, f2 in zip(check_outputs1, check_outputs2):
        assert circuit1[f1].equivalent(circuit2[f2])  # type: ignore


@pytest.mark.parametrize("input_file", ["test_add_delete.json"])
def test_add_delete(input_file: str):
    graph = InverterGraph.from_json(f"tests/verification/{input_file}")

    inputs = graph.inputs.copy()
    graph.add_input("test_input")
    print(graph.inputs)
    assert graph.inputs == inputs + ["test_input"]
    graph.delete_input("test_input")
    assert graph.inputs == inputs

    outputs = graph.outputs.copy()
    graph.add_output("f2")
    assert graph.outputs == outputs + ["f2"]
    graph.delete_output("f2")
    assert graph.outputs == outputs

    nodes = list(graph.nodes.keys())
    new_node = Node("and", ["1", 1, "1", 1])
    name = graph.add_node(new_node)
    assert list(graph.nodes.keys()) == nodes + [name]
    assert graph.nodes[name] == new_node
    graph.delete_node(name)
    assert list(graph.nodes.keys()) == nodes


@pytest.mark.parametrize(
    "input_file, root, expected_formula",
    [
        ("test_aig_inputs.json", "x1", exprvar("x1")),  # type: ignore
        ("test_aig_inputs.json", "x2", exprvar("x2")),  # type: ignore
        ("test_aig_4.json", "f", exprvar("x1") & exprvar("x2") & exprvar("x3")),  # type: ignore
        ("test_aig_4.json", "y1", exprvar("x1") & exprvar("x2")),  # type: ignore
    ],
)
def test_construct_formula(input_file: str, root: str, expected_formula: BooleanFunction):
    """Tests construct_formula"""
    circuit = InverterGraph.from_json(f"tests/verification/{input_file}")
    formula: BooleanFunction = circuit.construct_formula(root)
    assert formula.equivalent(expected_formula)  # type: ignore
