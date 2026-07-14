import json
import os

from mk_eda.libs.verilog.parser import VerilogParser, VerilogParserResult


def read_file(filename: str) -> str:
    with open(filename) as file:
        return file.read().rstrip("\n")


def test_verilog_parser() -> None:
    test_files_dir: str = os.path.join(os.path.dirname(__file__), "data")
    test_files: list[str] = os.listdir(test_files_dir)
    parser: VerilogParser = VerilogParser()

    for test_file in test_files:
        if test_file.endswith(".v"):
            test_file_path: str = os.path.join(test_files_dir, test_file)
            expected_json_path: str = test_file_path.replace(".v", ".expected.json")

            verilog_code: str = read_file(test_file_path)
            result: VerilogParserResult = parser.parse(verilog_code)
            result_json_string: str = json.dumps((result.keyword, result.module_name, result.names, result.nodes))
            expected_result: str = read_file(expected_json_path)
            assert result_json_string == expected_result
