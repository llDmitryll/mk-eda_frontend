from __future__ import annotations

from pathlib import Path

import pytest

from mk_eda.libs.aig.aig import AndInverterGraph
from mk_eda.libs.common.constants import PROJECT_DIR
from mk_eda.libs.optimization.rewriting import AIGRewriter

TEST_FILES_DIR = Path(__file__).parent / "rewriting_data"
JSONS_DIR = PROJECT_DIR / Path("tests/verification")


@pytest.mark.parametrize(
    "file_name, expected",
    [
        (
            "test_opt_aig_1.json",
            "test_aig_1_d.json",
        ),
    ],
)
def test_change_to_null(file_name: str, expected: str):
    """Tests deleting null nodes"""
    aig = AndInverterGraph.from_json(str(TEST_FILES_DIR / file_name))
    opt_aig = AIGRewriter()
    opt_aig.change_to_null(aig)
    assert aig.nodes == AndInverterGraph.from_json(str(JSONS_DIR / expected)).nodes


@pytest.mark.parametrize(
    "file_name, expected",
    [
        ("test_opt_aig_2.json", "test_aig_1_d.json"),
    ],
)
def test_delete_equals(file_name: str, expected: str):
    """Tests deleting equal nodes"""
    aig = AndInverterGraph.from_json(str(TEST_FILES_DIR / file_name))
    opt_aig = AIGRewriter()
    opt_aig.delete_equal_nodes(aig)
    assert aig.nodes == AndInverterGraph.from_json(str(JSONS_DIR / expected)).nodes


@pytest.mark.parametrize(
    "file_name, expected",
    [
        (
            "test_opt_aig_1_d.json",
            "test_opt_aig_3.json",
        ),
    ],
)
def test_make_absorption(file_name: str, expected: str):
    """Tests absorbing"""
    aig = AndInverterGraph.from_json(str(TEST_FILES_DIR / file_name))
    opt_aig = AIGRewriter()
    opt_aig.make_absorption(aig)
    assert aig.nodes == AndInverterGraph.from_json(str(TEST_FILES_DIR / expected)).nodes


@pytest.mark.parametrize(
    "file_name, expected",
    [
        ("test_opt_aig_4.json", "test_aig_2_g.json"),
    ],
)
def test_delete_inverse_and_idempotent(file_name: str, expected: str):
    """Tests deleting inverse and idempotent"""
    aig = AndInverterGraph.from_json(str(TEST_FILES_DIR / file_name))
    opt_aig = AIGRewriter()
    opt_aig.delete_inverse_and_idempotent(aig)
    assert aig.nodes == AndInverterGraph.from_json(str(JSONS_DIR / expected)).nodes


@pytest.mark.parametrize(
    "file_name, expected",
    [
        ("test_opt_aig_5.json", "test_opt_aig_6.json"),
    ],
)
def test_delete_identical(file_name: str, expected: str):
    """Tests deleting identical"""
    aig = AndInverterGraph.from_json(str(TEST_FILES_DIR / file_name))
    opt_aig = AIGRewriter()
    opt_aig.delete_identical(aig)
    assert aig.nodes == AndInverterGraph.from_json(str(TEST_FILES_DIR / expected)).nodes
