import json
import os

import pytest

from mk_eda.libs.common.constants import PROJECT_DIR
from mk_eda.libs.graph.graph import InverterGraph, RawGraph
from mk_eda.libs.verification.partitioner.depth.depth_partitioner import depth_partitioner


@pytest.mark.parametrize(
    "json_file, depth, expected_result",
    [
        (
            "test_part_d_1.json",
            1,
            "test_part_d_1_expected_1.json",
        ),
        (
            "test_part_d_1.json",
            2,
            "test_part_d_1_expected_2.json",
        ),
        (
            "test_part_d_2.json",
            3,
            "test_part_d_2_expected_3.json",
        ),
        (
            "test_part_d_2.json",
            2,
            "test_part_d_2_expected_2.json",
        ),
        (
            "test_part_d_3.json",
            2,
            "test_part_d_3_expected_2.json",
        ),
        (
            "test_part_d_3.json",
            3,
            "test_part_d_3_expected_3.json",
        ),
        (
            "test_part_d_4.json",
            4,
            "test_part_d_4_expected_4.json",
        ),
        (
            "test_part_d_5.json",
            4,
            "test_part_d_5_expected_4.json",
        ),
        (
            "test_part_d_5.json",
            8,
            "test_part_d_5_expected_8.json",
        ),
    ],
)
def test_depth_partitioner(json_file: str, depth: int, expected_result: str):
    """Test checking equivalence of circuits."""
    file_path = os.path.join(PROJECT_DIR, "mk_eda/libs/verification/partitioner/depth/tests/data", json_file)
    file_path_result = os.path.join(
        PROJECT_DIR, "mk_eda/libs/verification/partitioner/depth/tests/data", expected_result
    )

    in_graph = InverterGraph.from_json(file_path)
    partition = depth_partitioner(in_graph, int(depth))

    file = open(file_path_result)
    graph_raw_list: list[RawGraph] = json.load(file)
    file.close()
    partition_raw: list[RawGraph] = []
    for elem in partition:
        partition_raw.append(elem._to_raw())  # type: ignore
    assert partition_raw.sort(key=lambda x: x["inputs"]) == graph_raw_list.sort(key=lambda x: x["inputs"])
