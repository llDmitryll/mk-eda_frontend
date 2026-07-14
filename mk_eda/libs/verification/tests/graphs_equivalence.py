from collections import Counter
from typing import Optional

from mk_eda.libs.verification.tests.inverse_graph import InverseGraph


# Функция, проверяющая эквивалентности выходных вершин двух графов.
# Эта функция проверяет, можно ли биективно сопоставить
# друг другу вершины двух графов
# с условием одинакового класса эквивалентности
def check_equivalences(
    outputs1_val: dict[str, list[int]], outputs2_val: dict[str, list[int]], outputs1: list[str], outputs2: list[str]
) -> bool:
    return Counter(str(outputs1_val[i]) for i in outputs1) == Counter(str(outputs2_val[i]) for i in outputs2)


# Функция, с помощью перебора тестов из tests
# определяющая эквивалентность двух графов и выдающая либо None,
# в случае эквивалентности, либо набор на котором они отличаются
def check_circuits_equivalences(
    graph1: InverseGraph, graph2: InverseGraph, tests: list[list[int]]
) -> Optional[list[int]]:
    outputs1 = graph1.outputs
    outputs2 = graph2.outputs

    # Прогоняются все тесты из tests,
    # вершинам присваиваются соответствующие значения
    for test in tests:
        graph1.set_input_values(test)
        graph2.set_input_values(test)

        for root in outputs1:
            graph1.fill_value(root)
        for root in outputs2:
            graph2.fill_value(root)

        if not check_equivalences(graph1.vertex_classes, graph2.vertex_classes, outputs1, outputs2):
            graph1.clear_vertex_values()
            graph2.clear_vertex_values()
            return test

        graph1.clear_vertex_values()
        graph2.clear_vertex_values()


# Функция, создающая файл,
# хранящий список пар потенциально эквивалентных вершин схем
def find_equivalent_vertex_pairs(
    vertices1_val: dict[str, list[int]], vertices2_val: dict[str, list[int]]
) -> list[tuple[str, str]]:
    class_vertices_1 = build_class_vertices(vertices1_val)
    class_vertices_2 = build_class_vertices(vertices2_val)
    pairs_eq_vertices: list[tuple[str, str]] = []

    for key, vertices1 in class_vertices_1.items():
        if vertices2 := class_vertices_2.get(key):
            for vert1 in vertices1:
                for vert2 in vertices2:
                    pairs_eq_vertices.append((vert1, vert2))

    return pairs_eq_vertices


def build_class_vertices(vertices_val: dict[str, list[int]]) -> dict[tuple[int, ...], list[str]]:
    class_vertices: dict[tuple[int, ...], list[str]] = {}
    for v, cl in vertices_val.items():
        key = tuple(cl)
        if key in class_vertices:
            class_vertices[key].append(v)
        else:
            class_vertices[key] = [v]

    return class_vertices
