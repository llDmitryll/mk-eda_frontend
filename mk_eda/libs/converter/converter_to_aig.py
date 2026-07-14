import json
import math
import re
from pathlib import Path
from typing import Literal, Union

from mk_eda.libs.aig.aig import AndInverterGraph
from mk_eda.libs.graph.graph import Child, RawGraph


def convert_binary_vectors_to_aig(file_path: Path, output_path: Path) -> None:
    with open(file_path) as file:
        functions = [line.strip() for line in file.readlines()]

    aig_results: dict[str, RawGraph] = {}

    for i, func in enumerate(functions):
        aig_results[f"function_{i + 1}"] = convert_vector_to_aig_dict(func, i)

    with open(output_path, "w") as json_file:
        json.dump(aig_results, json_file, indent=4)


def convert_vector_to_aig_dict(func_str: Union[str, list[Literal[0, 1]]], func_counter: int) -> RawGraph:
    if isinstance(func_str, list):
        func_str = "".join(map(str, func_str))

    if not re.match(r"^[01]+$", func_str):
        raise ValueError("Все значения должны быть 0 или 1.")

    length = len(func_str)
    if (length & (length - 1)) != 0:
        raise ValueError("Длина каждой функции должна быть 2^n.")

    aig_result = AndInverterGraph()
    num_variables = int(math.log2(length))

    for i in range(num_variables):
        aig_result.add_input(f"x{i + 1}")

    add_nodes(aig_result, func_str, func_counter)

    return aig_result._to_raw()  # type: ignore


def add_nodes(aig_result: AndInverterGraph, func_str: str, func_counter: int) -> None:
    length = len(func_str)
    num_variables = int(math.log2(length))

    intermediate_count = 0
    clauses: list[Child] = []

    num_ones = func_str.count("1")
    num_zeros = len(func_str) - num_ones

    if num_zeros == len(func_str):
        aig_result.add_output("0")
        return

    if num_ones == len(func_str):
        aig_result.add_output("1")
        return

    if func_str == "01":
        aig_result.add_output("x1")
        return

    if func_str == "10":
        aig_result.add_output(f"f{func_counter + 1}")
        aig_result.f_and(Child("x1", False), Child("x1", False), f"f{func_counter + 1}")
        return

    is_cnf = (num_ones >= num_zeros and num_ones != len(func_str)) or num_ones == 0

    for idx, bit in enumerate(func_str):
        if (bit == "1") == is_cnf:
            continue

        input_clauses: list[Child] = []
        for var_index in range(num_variables):
            var_name = f"x{var_index + 1}"
            if idx & (1 << (num_variables - var_index - 1)):
                input_clauses.append(Child(var_name, True))
            else:
                input_clauses.append(Child(var_name, False))

        while len(input_clauses) > 1:
            left = input_clauses.pop(0)
            right = input_clauses.pop(0)
            intermediate_count += 1
            node_name = f"y{intermediate_count}"
            aig_result.f_and(left, right, node_name)
            input_clauses.insert(0, Child(node_name, True))

        clauses.append(input_clauses[0])

    len_clauses = len(clauses)

    while len(clauses) > 1:
        left = clauses.pop(0)
        right = clauses.pop(0)
        intermediate_count += 1
        node_name = f"y{intermediate_count}"
        if len_clauses == len(clauses) + 2:
            aig_result.f_and(Child(left.name, False), Child(right.name, False))
        else:
            aig_result.f_and(Child(left.name, True), Child(right.name, False))
        clauses.insert(0, Child(node_name, True))

    if len(clauses) == 1 and ((not is_cnf and num_ones > 1) or num_zeros == 1):
        final_clause = clauses.pop(0)
        intermediate_count += 1
        node_name = f"y{intermediate_count}"
        aig_result.f_and(Child(final_clause.name, False), Child(final_clause.name, False))
        clauses.insert(0, Child(node_name, True))

    aig_result.add_output(f"f{func_counter + 1}")
    aig_result.nodes[f"f{func_counter + 1}"] = aig_result.nodes.pop(clauses[0].name)
