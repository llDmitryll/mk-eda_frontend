from itertools import product
from typing import Optional

from mk_eda.libs.functions.mincode_generator import MincodeData, MincodeGenerator
from mk_eda.libs.graph.graph import InverterGraph, NodeFactory
from mk_eda.libs.verilog.parser import VerilogParser, VerilogParserResult


def format_result(result: MincodeData, variables: list[str]) -> list[str]:
    formatted_data: list[str] = [""] * len(variables)
    for i, index in enumerate(result.permutation):
        if result.negations[i]:
            formatted_data[index] = "~" + variables[i]
        else:
            formatted_data[index] = variables[i]
    return formatted_data


class BooleanMatching:
    def check_matching(self, verilog_code1: str, verilog_code2: str) -> Optional[list[tuple[list[str], str, str]]]:
        function_dict1, inputs1 = self.parse_verilog(verilog_code1)
        function_dict2, inputs2 = self.parse_verilog(verilog_code2)

        mg = MincodeGenerator()

        mincodes1: list[tuple[MincodeData, str]] = []
        mincodes2: list[tuple[MincodeData, str]] = []
        for output in function_dict1:
            mincodes1.append(((mg.generate_mincode([int(boo) for boo in function_dict1[output]])), output))
        for output in function_dict2:
            mincodes2.append(((mg.generate_mincode([int(boo) for boo in function_dict2[output]])), output))

        possible_matches: Optional[list[tuple[list[str], str, str]]] = []
        for out1, output1_name in mincodes1:
            for out2, output2_name in mincodes2:
                if out1.function == out2.function:
                    fres1 = format_result(out1, inputs1)
                    fres2 = format_result(out2, inputs2)
                    matches: list[str] = []
                    if len(fres1) != len(fres2):
                        return []
                    for res1, res2 in zip(fres1, fres2):
                        if "~" in res1 and "~" in res2:
                            res1, res2 = res1.replace("~", ""), res2.replace("~", "")
                        matches.append(f"{res1} = {res2}")
                    possible_matches.append((matches, output1_name, output2_name))
        return possible_matches

    def parse_verilog(self, verilog_code: str) -> tuple[dict[str, list[bool]], list[str]]:
        verilog_parser = VerilogParser()

        verilog_result = verilog_parser.parse(verilog_code)
        graph_parsed = self.build_parsed_graph(verilog_result)
        function_dict = self.evaluate_graph(graph_parsed)
        return function_dict, graph_parsed.inputs

    def build_parsed_graph(self, verilog_result: VerilogParserResult) -> InverterGraph:
        graph_to_build = InverterGraph()
        negations: dict[str, str] = {}

        def node_to_child(name_to_check: str) -> tuple[str, bool]:
            return negations.get(name_to_check, name_to_check), name_to_check in negations

        for entry in verilog_result.nodes:
            node_type = entry[0]
            if node_type == "input":
                for input in entry[2]:
                    graph_to_build.add_input(input)

            elif node_type == "output":
                for output in entry[2]:
                    graph_to_build.add_output(output)

            elif node_type == "not":
                negations[entry[1][0][3][0]] = entry[1][0][3][1]

            elif node_type in NodeFactory.TWO_INPUT_NODES:
                elements = entry[1][0][3]
                name = elements[0]
                elements = elements[1:]

                first_node = NodeFactory.create([node_type, *node_to_child(elements[0]), *node_to_child(elements[1])])

                prev_output = graph_to_build.add_node(first_node, name=name if len(elements) <= 2 else None)

                if len(elements) <= 2:
                    continue
                last_index = len(elements) - 1
                for i, input_node in enumerate(elements[2:], start=2):
                    new_node = NodeFactory.create([node_type, *node_to_child(prev_output), *node_to_child(input_node)])
                    prev_output = graph_to_build.add_node(new_node, name=name if i == last_index else None)
        return graph_to_build

    def evaluate_graph(self, graph_to_evaluate: InverterGraph) -> dict[str, list[bool]]:
        inputs = graph_to_evaluate.inputs
        outputs = graph_to_evaluate.outputs
        output_dict: dict[str, list[bool]] = {}
        for input_values in product([False, True], repeat=len(inputs)):
            input_assignment = dict(zip(inputs, input_values))
            for output in outputs:
                output_value = graph_to_evaluate.evaluate(output, input_assignment)
                output_dict.setdefault(output, [])
                output_dict[output].append(output_value)
        return output_dict
