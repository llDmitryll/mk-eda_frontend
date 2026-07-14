import pytest

from mk_eda.libs.translate.translate_aig import AigDict, translate_aig


@pytest.mark.parametrize(
    "file_name,expected",
    [
        ("./mk_eda/libs/translate/tests/data/0.aag", {"inputs": [], "outputs": [], "nodes": {}}),
        (
            "./mk_eda/libs/translate/tests/data/1.aag",
            {
                "inputs": ["x1", "x2", "x3"],
                "outputs": ["f1"],
                "nodes": {"y1": ["and", "x1", 1, "x2", 0], "f1": ["and", "y1", 0, "x3", 1]},
            },
        ),
        (
            "./mk_eda/libs/translate/tests/data/2.aag",
            {
                "inputs": ["x1", "x2"],
                "outputs": ["f1"],
                "nodes": {
                    "y1": ["and", "x1", 1, "x2", 1],
                    "y2": ["and", "x2", 0, "x1", 0],
                    "f1": ["and", "y1", 0, "y2", 0],
                },
            },
        ),
        (
            "./mk_eda/libs/translate/tests/data/3.aag",
            {
                "inputs": ["x1", "x2", "x4"],
                "outputs": ["x1", "f1", "f2"],
                "nodes": {"f1": ["and", "x1", 1, "x2", 1], "f2": ["and", "x2", 1, "x4", 1]},
            },
        ),
        (
            "./mk_eda/libs/translate/tests/data/4.aag",
            {
                "inputs": ["x1", "x2"],
                "outputs": ["f1", "0"],
                "nodes": {
                    "f1": ["and", "y1", 1, "x2", 0],
                    "y1": ["and", "x1", 1, "y3", 1],
                    "y2": ["and", "x1", 1, "0", 1],
                    "y3": ["and", "1", 1, "x2", 1],
                },
            },
        ),
        (
            "./mk_eda/libs/translate/tests/data/5.aag",
            {"inputs": [], "outputs": [], "nodes": {"y1": ["and", "1", 1, "1", 1], "y2": ["and", "y1", 1, "y1", 0]}},
        ),
        (
            "./mk_eda/libs/translate/tests/data/6.aig",
            {
                "inputs": ["x1", "x2", "x3", "x4"],
                "outputs": ["f1"],
                "nodes": {
                    "y1": ["and", "x2", 0, "x1", 1],
                    "y2": ["and", "x4", 1, "x3", 0],
                    "f1": ["and", "y2", 1, "y1", 0],
                },
            },
        ),
        (
            "./mk_eda/libs/translate/tests/data/7.aig",
            {"inputs": ["x1", "x2"], "outputs": ["x1", "f1"], "nodes": {"f1": ["and", "x2", 1, "1", 1]}},
        ),
        (
            "./mk_eda/libs/translate/tests/data/8.aig",
            {"inputs": ["x1", "x2"], "outputs": ["f1"], "nodes": {"f1": ["and", "x1", 0, "x2", 1]}},
        ),
        (
            "./mk_eda/libs/translate/tests/data/9.aig",
            {"inputs": [], "outputs": ["f1"], "nodes": {"y1": ["and", "1", 1, "0", 1], "f1": ["and", "y1", 0, "1", 1]}},
        ),
        ("./mk_eda/libs/translate/tests/data/10.aag", {"inputs": ["x1"], "outputs": ["x1"], "nodes": {}}),
    ],
)
def test_translate_aig(file_name: str, expected: AigDict):
    assert translate_aig(file_name) == expected
