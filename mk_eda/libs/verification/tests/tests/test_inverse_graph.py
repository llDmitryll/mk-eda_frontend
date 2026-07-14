from typing import Union

import pytest

from mk_eda.libs.verification.tests.inverse_graph import InverseGraph


@pytest.mark.parametrize(
    "file_name, outputs, inputs, structure, values, classes",
    [
        (
            "test_aig_1_d.json",
            [
                "f",
            ],
            [
                "x1",
                "x2",
                "x3",
                "x4",
            ],
            {
                "const0": ("const",),
                "const1": ("const",),
                "x1": ("input",),
                "x2": ("input",),
                "x3": ("input",),
                "x4": ("input",),
                "y1": ("and", "x1", 1, "x2", 1),
                "y2": ("and", "y1", 1, "x3", 1),
                "f": ("and", "y2", 1, "x4", 1),
            },
            {
                "const0": 0,
                "const1": 1,
            },
            {
                "y1": [],
                "y2": [],
                "f": [],
            },
        ),
        (
            "test_aig_1_g.json",
            [
                "f",
            ],
            [
                "x1",
                "x2",
                "x3",
                "x4",
            ],
            {
                "const0": ("const",),
                "const1": ("const",),
                "x1": ("input",),
                "x2": ("input",),
                "x3": ("input",),
                "x4": ("input",),
                "y1": ("and", "x1", 0, "x2", 0),
                "y2": ("and", "y1", 0, "x3", 1),
                "f": ("and", "y2", 1, "x4", 1),
            },
            {
                "const0": 0,
                "const1": 1,
            },
            {
                "y1": [],
                "y2": [],
                "f": [],
            },
        ),
    ],
)
def test_creating_a_graph(
    file_name: str,
    outputs: list[str],
    inputs: list[str],
    structure: dict[str, tuple[Union[str, int], ...]],
    values: dict[str, int],
    classes: dict[str, list[int]],
):
    # tests for create all the tests
    graph = InverseGraph.from_json(file_name=f"tests/verification/{file_name}")
    assert graph.outputs == outputs
    assert graph.inputs == inputs
    assert graph.structure == structure
    assert graph.values == values
    assert graph.vertex_classes == classes


@pytest.mark.parametrize(
    "file_name, values",
    [
        ("test_aig_1_d.json", [0, 0, 0, 0]),
        ("test_aig_1_d.json", [0, 1, 0, 1]),
        ("test_aig_1_d.json", [1, 1, 1, 0]),
        ("test_aig_1_g.json", [0, 0, 0, 0]),
        ("test_aig_1_g.json", [0, 1, 0, 1]),
        ("test_aig_1_g.json", [1, 1, 1, 0]),
    ],
)
def test_set_input_values(file_name: str, values: list[int]):
    # tests for setting the values of inputs in the graph
    graph = InverseGraph.from_json(file_name=f"tests/verification/{file_name}")
    graph.set_input_values(values)
    for i, input in enumerate(graph.inputs):
        assert graph.values[input] == values[i]


@pytest.mark.parametrize(
    "file_name, start_vert, inputs_values, correct_values",
    [
        (
            "test_aig_1_d.json",
            "f",
            [0, 0, 0, 0],
            {
                "const0": 0,
                "const1": 1,
                "x1": 0,
                "x2": 0,
                "x3": 0,
                "x4": 0,
                "y1": 0,
                "y2": 0,
                "f": 0,
            },
        ),
        (
            "test_aig_1_d.json",
            "f",
            [1, 1, 0, 1],
            {
                "const0": 0,
                "const1": 1,
                "x1": 1,
                "x2": 1,
                "x3": 0,
                "x4": 1,
                "y1": 1,
                "y2": 0,
                "f": 0,
            },
        ),
        (
            "test_aig_1_g.json",
            "f",
            [0, 1, 1, 0],
            {
                "const0": 0,
                "const1": 1,
                "x1": 0,
                "x2": 1,
                "x3": 1,
                "x4": 0,
                "y1": 0,
                "y2": 1,
                "f": 0,
            },
        ),
        (
            "test_aig_1_g.json",
            "f",
            [1, 0, 1, 1],
            {
                "const0": 0,
                "const1": 1,
                "x1": 1,
                "x2": 0,
                "x3": 1,
                "x4": 1,
                "y1": 0,
                "y2": 1,
                "f": 1,
            },
        ),
    ],
)
def test_fill_value(file_name: str, start_vert: str, inputs_values: list[int], correct_values: dict[str, int]):
    graph = InverseGraph.from_json(file_name=f"tests/verification/{file_name}")
    graph.set_input_values(inputs_values)
    graph.fill_value(start_vert)
    for vert in correct_values.keys():
        assert graph.values[vert] == correct_values[vert]


@pytest.mark.parametrize(
    "file_name, start_vert, inputs_values",
    [
        (
            "test_aig_1_d.json",
            "f",
            [0, 0, 0, 0],
        ),
        (
            "test_aig_1_d.json",
            "y1",
            [0, 1, 0, 1],
        ),
        (
            "test_aig_1_g.json",
            "f",
            [1, 1, 0, 0],
        ),
        (
            "test_aig_1_g.json",
            "y2",
            [0, 0, 1, 1],
        ),
        (
            "test_aig_2_d.json",
            "f",
            [1, 0, 0, 1],
        ),
        (
            "test_aig_2_g.json",
            "f",
            [1, 1, 1, 1],
        ),
    ],
)
def test_clear_graph(file_name: str, start_vert: str, inputs_values: list[int]):
    correct_values: dict[str, int] = {"const0": 0, "const1": 1}
    graph = InverseGraph.from_json(file_name=f"tests/verification/{file_name}")
    graph.set_input_values(inputs_values)
    graph.fill_value(start_vert)
    graph.clear_vertex_values()
    assert graph.values == correct_values
