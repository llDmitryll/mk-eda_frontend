from typing import Optional

import pytest

from mk_eda.libs.verification.tests.graphs_equivalence import (
    check_circuits_equivalences,
    check_equivalences,
    find_equivalent_vertex_pairs,
)
from mk_eda.libs.verification.tests.inverse_graph import InverseGraph


@pytest.mark.parametrize(
    "classes1, classes2, outputs1, outputs2, result",
    [
        (
            {
                "out1": [1, 1, 1],
                "out2": [1, 1, 0],
                "out3": [1, 0, 0],
            },
            {
                "out4": [1, 0, 0],
                "out5": [1, 1, 0],
                "out6": [1, 1, 1],
            },
            ["out1", "out2", "out3"],
            ["out4", "out5", "out6"],
            True,
        ),
        (
            {
                "neg": [0, 0, 0],
                "out1": [1, 1, 1],
                "out2": [1, 1, 0],
                "pos": [1, 1, 1],
                "out3": [1, 0, 0],
            },
            {
                "out4": [1, 0, 0],
                "out5": [1, 1, 0],
                "out6": [1, 1, 1],
                "end_out": [0, 0, 1],
            },
            ["out1", "out2", "out3"],
            ["out4", "out5", "out6"],
            True,
        ),
        (
            {
                "neg": [0, 0, 0],
                "out1": [1, 1, 1],
                "out2": [1, 1, 0],
                "pos": [1, 1, 1],
            },
            {
                "out3": [1, 0, 0],
                "out4": [1, 1, 0],
                "out5": [1, 1, 1],
                "end_out": [0, 0, 1],
            },
            ["out1", "out2"],
            ["out3", "out4", "out5"],
            False,
        ),
        (
            {
                "out1": [1, 1, 1],
                "out2": [1, 1, 0],
                "out3": [1, 0, 1],
                "out4": [1, 1, 1],
            },
            {
                "out1": [1, 1, 1],
                "out2": [1, 0, 1],
                "out3": [1, 0, 1],
                "out4": [1, 1, 0],
            },
            ["out1", "out2", "out3", "out4"],
            ["out1", "out2", "out3", "out4"],
            False,
        ),
    ],
)
def test_check_equivalences(
    classes1: dict[str, list[int]],
    classes2: dict[str, list[int]],
    outputs1: list[str],
    outputs2: list[str],
    result: bool,
):
    assert check_equivalences(classes1, classes2, outputs1, outputs2) == result


@pytest.mark.parametrize(
    "file_name1, file_name2, tests, result",
    [
        (
            "test_aig_1_d.json",
            "test_aig_1_g.json",
            [
                [0, 0, 0, 0],
                [0, 1, 0, 1],
                [1, 1, 1, 1],
                [1, 0, 1, 1],
                [0, 1, 1, 1],
            ],
            [1, 0, 1, 1],
        ),
        (
            "test_aig_1_d.json",
            "test_aig_1_g.json",
            [
                [0, 0, 1, 1],
                [1, 1, 1, 0],
                [1, 1, 1, 1],
                [1, 0, 0, 1],
                [0, 1, 1, 0],
            ],
            None,
        ),
        (
            "test_aig_1_d.json",
            "test_aig_1_g.json",
            [
                [0, 1, 1, 1],
            ],
            [0, 1, 1, 1],
        ),
        (
            "test_aig_1_d.json",
            "test_aig_1_d.json",
            [
                [0, 0, 0, 0],
                [0, 1, 0, 1],
                [1, 1, 1, 1],
                [1, 0, 1, 1],
                [0, 1, 1, 1],
            ],
            None,
        ),
        (
            "test_aig_1_d.json",
            "test_aig_1_d.json",
            [],
            None,
        ),
        (
            "test_aig_1_d.json",
            "test_aig_1_d.json",
            [
                [0, 0, 0, 0],
                [0, 0, 0, 1],
                [0, 0, 1, 0],
                [0, 0, 1, 1],
                [0, 1, 0, 0],
                [0, 1, 0, 1],
                [0, 1, 1, 0],
                [0, 1, 1, 1],
                [1, 0, 0, 0],
                [1, 0, 0, 1],
                [1, 0, 1, 0],
                [1, 0, 1, 1],
                [1, 1, 0, 0],
                [1, 1, 0, 1],
                [1, 1, 1, 0],
                [1, 1, 1, 1],
            ],
            None,
        ),
    ],
)
def test_check_circuits_equivalences(
    file_name1: str, file_name2: str, tests: list[list[int]], result: Optional[list[int]]
):
    graph1 = InverseGraph.from_json(file_name=f"tests/verification/{file_name1}")
    graph2 = InverseGraph.from_json(file_name=f"tests/verification/{file_name2}")
    assert check_circuits_equivalences(graph1, graph2, tests) == result


@pytest.mark.parametrize(
    "vertex1, vertex2, correct_pairs",
    [
        (
            {
                "v1": [1, 0, 1],
                "v2": [1, 1, 1],
                "v3": [0, 0, 0],
                "v4": [0, 0, 1],
            },
            {
                "v5": [1, 0, 1],
                "v6": [1, 0, 0],
                "v7": [0, 1, 0],
                "v8": [1, 1, 1],
            },
            [
                ("v1", "v5"),
                ("v2", "v8"),
            ],
        ),
        (
            {
                "v1": [1, 1, 1],
                "v2": [1, 1, 0],
                "v3": [1, 0, 0],
                "v4": [1, 0, 1],
            },
            {
                "v5": [0, 0, 1],
                "v6": [0, 0, 0],
                "v7": [0, 1, 0],
                "v8": [0, 1, 1],
            },
            [],
        ),
        (
            {
                "v1": [1, 1, 1],
                "v2": [1, 1, 1],
            },
            {
                "v3": [1, 0, 1],
                "v4": [1, 0, 0],
                "v5": [0, 1, 0],
                "v6": [1, 0, 1],
                "v7": [1, 1, 1],
            },
            [
                ("v1", "v7"),
                ("v2", "v7"),
            ],
        ),
        (
            {
                "v1": [0, 0, 1],
                "v2": [1, 1, 1],
                "v3": [0, 0, 1],
            },
            {
                "v4": [0, 0, 1],
                "v5": [0, 0, 1],
                "v6": [0, 1, 0],
            },
            [
                ("v1", "v4"),
                ("v1", "v5"),
                ("v3", "v4"),
                ("v3", "v5"),
            ],
        ),
    ],
)
def test_find_equivalent_vertex_pairs(
    vertex1: dict[str, list[int]], vertex2: dict[str, list[int]], correct_pairs: list[tuple[str]]
):
    assert find_equivalent_vertex_pairs(vertex1, vertex2) == correct_pairs
