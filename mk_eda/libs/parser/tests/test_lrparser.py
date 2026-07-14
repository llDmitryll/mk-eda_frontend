import json
import os

from mk_eda.libs.graph.graph import InverterGraph, nodes_to_raw
from mk_eda.libs.parser.parser import VerilogGrammar


def read_file(filename: str) -> str:
    with open(filename) as file:
        return file.read().rstrip("\n")


def test_verilog_parser() -> None:
    test_files_dir: str = os.path.join(os.path.dirname(__file__), "data")
    test_files: list[str] = os.listdir(test_files_dir)
    parser: VerilogGrammar = VerilogGrammar()
    for test_file in test_files:
        if test_file.endswith(".v"):
            test_file_path: str = os.path.join(test_files_dir, test_file)
            verilog_code: str = read_file(test_file_path)
            result_graph: InverterGraph = parser.lrparse(verilog_code)
            expected_file = test_file_path.replace(".v", "_expected.json")
            file = open(expected_file)
            expected_graph = json.load(file)
            assert expected_graph["inputs"] == result_graph.inputs
            assert expected_graph["outputs"] == result_graph.outputs
            assert expected_graph["nodes"] == nodes_to_raw(result_graph.nodes)
            file.close()
