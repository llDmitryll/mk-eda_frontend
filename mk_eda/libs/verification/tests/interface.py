import json
from typing import Optional

from mk_eda.libs.verification.tests.graphs_equivalence import check_circuits_equivalences, find_equivalent_vertex_pairs
from mk_eda.libs.verification.tests.inverse_graph import InverseGraph
from mk_eda.libs.verification.tests.tests_generator import create_all_tests, generating_tests, random_selection_of_tests


class Interface:
    def __init__(self):
        # Результат проверки на эквивалентность двух схем
        self.output: Optional[list[int]] = None
        # Флаг, который = True, если установлена эквивалентность двух схем, и False иначе
        self.flag_eq: bool = False

    @classmethod
    def run(cls, input_file_name1: str, input_file_name2: str, output_file_name: str) -> None:
        interface = cls()

        # Создание инверсных графов
        graph1 = InverseGraph.from_json(input_file_name1)
        graph2 = InverseGraph.from_json(input_file_name2)

        inputs = graph1.inputs
        tests_number = 1
        inputs_number = len(inputs)
        remaining_tests = []
        passed_tests = []
        if inputs_number <= 10:
            remaining_tests = create_all_tests(inputs_number)
        tests = []
        while tests_number and interface.output is None:
            if interface.flag_eq:
                break
            tests_number = interface._input_tests_number()
            if inputs_number <= 10:
                tests, remaining_tests = random_selection_of_tests(tests_number, remaining_tests)
                interface.output = check_circuits_equivalences(graph1, graph2, tests)
                if not interface.output and not remaining_tests:
                    interface.flag_eq = True
            else:
                tests, passed_tests = generating_tests(inputs_number, tests_number, passed_tests)
                interface.output = check_circuits_equivalences(graph1, graph2, tests)

        pairs_eq_vertices = find_equivalent_vertex_pairs(graph1.vertex_classes, graph2.vertex_classes)
        interface._print_output(pairs_eq_vertices)

        if output_file_name:
            interface._save_equivalent_vertices(pairs_eq_vertices, output_file_name)

    # Функция, запрашивающая следующее число тестов, на которых
    # нужно проверить эквивалентность 2 схем
    def _input_tests_number(self) -> int:
        print("How many tests do you want to use?")
        print("If you want to finish work, enter 0")
        return int(input())

    def _save_equivalent_vertices(self, pairs_eq_vertices: list[tuple[str, str]], output_file_name: str) -> None:
        with open(output_file_name, "w") as f:
            json.dump(pairs_eq_vertices, f)

    # Функция вывода
    def _print_output(self, pairs_eq_vertices: list[tuple[str, str]]) -> None:
        if self.flag_eq:
            print("These 2 circuits are equivalent")
        elif self.output is None:
            print("Not enough information")
        else:
            print("These 2 circuits are not equivalent on set", self.output)
            return
        print()
        print("Equivalent vertices:", pairs_eq_vertices)
