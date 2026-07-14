import pytest

from mk_eda.libs.graph.graph import Node, RawGraph
from mk_eda.libs.optimization.xaig_depth_optimizer import XAIGDepthOptimizer
from mk_eda.libs.xaig.xaig import XorAndInverterGraph


@pytest.mark.parametrize(
    "xaig,expected",
    [
        (
            {
                "inputs": ["x1", "x2", "x3", "x4"],
                "outputs": ["f1"],
                "nodes": {
                    "y1": ["xor", "x1", 0, "x2", 1],
                    "y2": ["xor", "y1", 1, "x3", 1],
                    "f1": ["xor", "y2", 1, "x4", 1],
                },
            },
            {
                "inputs": ["x1", "x2", "x3", "x4"],
                "outputs": ["f1"],
                "nodes": {
                    "y1": ["xor", "x1", 0, "x2", 1],
                    "y3": ["xor", "x3", 1, "x4", 1],
                    "f1": ["xor", "y1", 1, "y3", 1],
                },
            },
        ),
        (
            {
                "inputs": ["x1", "x2", "x3", "x4"],
                "outputs": ["f1", "x3"],
                "nodes": {
                    "y1": ["xor", "x1", 1, "x2", 1],
                    "y2": ["xor", "y1", 1, "x3", 1],
                    "f1": ["xor", "y2", 0, "x4", 1],
                },
            },
            {
                "inputs": ["x1", "x2", "x3", "x4"],
                "outputs": ["f1", "x3"],
                "nodes": {
                    "y1": ["xor", "x1", 1, "x2", 1],
                    "y2": ["xor", "y1", 1, "x3", 1],
                    "f1": ["xor", "y2", 0, "x4", 1],
                },
            },
        ),
        (
            {
                "inputs": ["x1", "x2"],
                "outputs": ["f1"],
                "nodes": {
                    "y1": ["xor", "x1", 1, "x1", 1],
                    "y2": ["xor", "x2", 1, "x2", 0],
                    "f1": ["and", "y1", 1, "y2", 1],
                },
            },
            {"inputs": ["x1", "x2"], "outputs": ["f1"], "nodes": {"f1": ["and", "0", 1, "1", 1]}},
        ),
        (
            {
                "inputs": ["x1", "x2"],
                "outputs": ["f1"],
                "nodes": {
                    "y1": ["and", "x1", 1, "x1", 1],
                    "y2": ["and", "x2", 1, "x2", 0],
                    "f1": ["and", "y1", 1, "y2", 1],
                },
            },
            {"inputs": ["x1", "x2"], "outputs": ["f1"], "nodes": {"f1": ["and", "x1", 1, "0", 1]}},
        ),
        (
            {
                "inputs": ["x1", "x2", "x3", "x4", "x5", "x6", "x7"],
                "outputs": ["f1", "f2", "f3", "f4", "f5", "f6", "f7"],
                "nodes": {
                    "f1": ["and", "x1", 1, "x1", 1],
                    "f2": ["and", "x2", 0, "x2", 0],
                    "f3": ["and", "1", 1, "x3", 1],
                    "f4": ["and", "x4", 1, "0", 0],
                    "f5": ["and", "x5", 1, "0", 1],
                    "f6": ["and", "x6", 1, "1", 0],
                    "f7": ["and", "x7", 1, "x7", 0],
                },
            },
            {
                "inputs": ["x1", "x2", "x3", "x4", "x5", "x6", "x7"],
                "outputs": ["f2", "x1", "x3", "x4", "0"],
                "nodes": {"f2": ["and", "x2", 0, "x2", 0]},
            },
        ),
        (
            {
                "inputs": ["x1", "x2", "x3", "x4", "x5", "x6", "x7"],
                "outputs": ["f1", "f2", "f3", "f4", "f5", "f6", "f7"],
                "nodes": {
                    "f1": ["xor", "x1", 1, "0", 1],
                    "f2": ["xor", "x2", 1, "1", 1],
                    "f3": ["xor", "x3", 0, "0", 1],
                    "f4": ["xor", "x4", 0, "1", 1],
                    "f5": ["xor", "x5", 1, "1", 0],
                    "f6": ["xor", "x6", 1, "x6", 1],
                    "f7": ["xor", "x7", 1, "x7", 0],
                },
            },
            {
                "inputs": ["x1", "x2", "x3", "x4", "x5", "x6", "x7"],
                "outputs": ["f2", "f3", "x1", "x4", "x5", "0", "1"],
                "nodes": {"f2": ["xor", "x2", 1, "1", 1], "f3": ["xor", "x3", 0, "0", 1]},
            },
        ),
    ],
)
def test_optimize(xaig: RawGraph, expected: RawGraph):
    aig = XorAndInverterGraph()
    for in_var in xaig["inputs"]:
        aig.add_input(in_var)
    for out_node in xaig["outputs"]:
        aig.add_output(out_node)
    for name, node in xaig["nodes"].items():
        print(name, aig.nodes)
        aig.add_node(Node(str(node[0]), node[1:]), name)

    test = XorAndInverterGraph()
    for in_var in expected["inputs"]:
        test.add_input(in_var)
    for out_node in expected["outputs"]:
        test.add_output(out_node)
    for name, node in expected["nodes"].items():
        test.add_node(Node(str(node[0]), node[1:]), name)

    opt_xaig = XAIGDepthOptimizer()
    aig = opt_xaig(aig)
    assert aig.inputs == test.inputs
    assert aig.outputs == test.outputs
    assert aig.nodes == test.nodes
