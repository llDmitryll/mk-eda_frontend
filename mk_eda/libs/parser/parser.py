from __future__ import annotations

from typing import Any

from lrparsing import Grammar, Keyword, List, Opt, Prio, Ref, Token  # type: ignore

from mk_eda.libs.graph.graph import InverterGraph, NodeFactory


class VerilogGrammar(Grammar):
    MODULE = Keyword("module")
    END_MODULE = Keyword("endmodule")
    INPUT = Keyword("input")
    OUTPUT = Keyword("output")
    WIRE = Keyword("wire")
    AND = Keyword("and")
    OR = Keyword("or")
    XOR = Keyword("xor")
    NOT = Keyword("not")
    ASSIGN = Keyword("assign")
    IDENTIFIER = Token(re="[a-zA-Z_][a-zA-Z0-9_]*")
    COMMA = Token(",")
    NUMBER = Token(re="[0-9]+")
    SEMICOLON = Token(";")
    L_PAREN = Token("(")
    R_PAREN = Token(")")
    L_BRACKET = Token("[")
    R_BRACKET = Token("]")
    L_BRACE = Token("{")
    R_BRACE = Token("}")
    EQUALS = Token("=")
    COLON = Token(":")

    expression = Prio(
        NUMBER,
        IDENTIFIER,
        IDENTIFIER + L_BRACKET + Ref("expression") + R_BRACKET,
        IDENTIFIER + L_BRACKET + Ref("expression") + COLON + Ref("expression") + R_BRACKET,
        Ref("concatenation"),
    )

    list_of_expressions = List(Ref("expression"), (Opt(COMMA)))
    concatenation = L_BRACE + list_of_expressions + R_BRACE

    assignment = Ref("lvalue") + EQUALS + Ref("expression")
    list_of_assignments = List(assignment, Opt(COMMA))
    continuous_assign = ASSIGN + list_of_assignments + SEMICOLON
    lvalue = Prio(
        IDENTIFIER,
        IDENTIFIER + L_BRACKET + Ref("expression") + R_BRACKET,
        IDENTIFIER + L_BRACKET + Ref("expression") + COLON + Ref("expression") + R_BRACKET,
        Ref("concatenation"),
    )

    range = L_BRACKET + Ref("expression") + COLON + Ref("expression") + R_BRACKET
    list_of_variables = List(IDENTIFIER, Opt(COMMA))

    input_declaration = INPUT + Opt(WIRE) + Prio(range + list_of_variables, list_of_variables) + SEMICOLON
    output_declaration = OUTPUT + Opt(WIRE) + Prio(range + list_of_variables, list_of_variables) + SEMICOLON
    net_declaration = WIRE + Prio(range + list_of_variables, list_of_variables) + SEMICOLON

    gate_type = Prio(AND, OR, XOR, NOT)
    gate_instance = Prio(
        IDENTIFIER + Ref("range") + L_PAREN + list_of_expressions + R_PAREN,
        IDENTIFIER + L_PAREN + list_of_expressions + R_PAREN,
        L_PAREN + list_of_expressions + R_PAREN,
    )
    list_of_gate_instances = List(gate_instance, Opt(COMMA))
    gate_declaration = Ref("gate_type") + list_of_gate_instances + SEMICOLON

    module_item = Prio(input_declaration, output_declaration, net_declaration, gate_declaration, continuous_assign)
    list_of_items = List(module_item, Opt(COMMA))
    list_of_ports = List((IDENTIFIER | INPUT | OUTPUT), Opt(COMMA))
    port_declaration = (L_PAREN + list_of_ports + R_PAREN) | (
        L_PAREN + input_declaration + output_declaration + R_PAREN
    )

    module = MODULE + IDENTIFIER + port_declaration + SEMICOLON + List(Ref("module_item"), Opt(COMMA)) + END_MODULE
    START = module

    def lrparse(self, verilog_code: str) -> InverterGraph:
        parse_result: Any = self.parse(verilog_code)  # type: ignore
        return self._build_graph(parse_result)

    def _build_graph(self, result: Any) -> InverterGraph:
        negations: dict[str, str] = {}
        inverter_graph = InverterGraph()

        _, module = result
        for rule, *args in module[3:]:
            if rule.name == "port_declaration":
                self._process_ports(args[1], inverter_graph)
            if rule.name == "module_item":
                self._process_module_item(args[0], negations, inverter_graph)

        return inverter_graph

    def _process_ports(self, ports: Any, inverter_graph: InverterGraph) -> None:
        port_type: str | None = None
        for rule, port in ports[1:]:
            if rule.name in {"INPUT", "OUTPUT"}:
                port_type = rule.name
            elif rule.name == "IDENTIFIER":
                if port_type == "INPUT":
                    inverter_graph.add_input(port[1])
                if port_type == "OUTPUT":
                    inverter_graph.add_output(port[1])

    def _process_module_item(self, module_item: Any, negations: dict[str, str], inverter_graph: InverterGraph) -> None:
        module_item_rule, *module_item_args = module_item

        if module_item_rule.name in {"input_declaration", "output_declaration"}:
            for io_rule, *io_args in module_item_args:
                if io_rule.name != "list_of_variables":
                    continue

                for wire_rule, wire_name in io_args:
                    if wire_rule.name != "IDENTIFIER":
                        continue

                    if module_item_rule.name == "input_declaration":
                        inverter_graph.add_input(wire_name[1])
                    else:
                        inverter_graph.add_output(wire_name[1])

        elif module_item_rule.name == "gate_declaration":
            gate_type = ""
            for gate_rule, subtree in module_item_args:
                if gate_rule.name == "gate_type":
                    gate_type = self._get_gate_type(subtree)
                elif gate_rule.name == "list_of_gate_instances":
                    self._process_gate_instances(subtree, gate_type, negations, inverter_graph)

    def _process_gate_instances(
        self, subtree: Any, gate_type: str, negations: dict[str, str], inverter_graph: InverterGraph
    ) -> None:
        def _node_to_child(name_to_check: str) -> tuple[str, bool]:
            return negations.get(name_to_check, name_to_check), name_to_check in negations

        _, _, instance, _ = subtree

        if gate_type == "not":
            _, neg_name, _, affected = instance
            negations[self._get_identifier(neg_name)] = self._get_identifier(affected)
            return

        tmp_node: list[str] = []
        if gate_type in {"and", "or", "xor"}:
            for rule, identifier in instance[1:]:
                if rule.name == "expression":
                    tmp_node.append(identifier[1][1])

            name = tmp_node[0]
            first_node = NodeFactory.create(
                [gate_type.lower(), *_node_to_child(tmp_node[1]), *_node_to_child(tmp_node[2])]
            )
            prev_output = inverter_graph.add_node(first_node, name=name if len(tmp_node) <= 3 else None)

            if len(tmp_node) <= 3:
                return

            last_index = len(tmp_node) - 1
            for i, input_node in enumerate(tmp_node[3:], start=3):
                new_node = NodeFactory.create(
                    [gate_type.lower(), *_node_to_child(prev_output), *_node_to_child(input_node)]
                )
                prev_output = inverter_graph.add_node(new_node, name=name if i == last_index else None)

    def _get_gate_type(self, subtree: Any) -> str:
        return subtree[1][1]

    def _get_identifier(self, subtree: Any) -> str:
        return subtree[1][1][1]
