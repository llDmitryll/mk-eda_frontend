from __future__ import annotations

import json
from functools import reduce


class InverseGraph:
    def __init__(self):
        # Список имен вершин-стоков (выходов)
        self.outputs: list[str] = []
        # Список имен вершин-истоков (входов)
        self.inputs: list[str] = []
        # Словарь, в котором каждой вершине сопоставляется кортеж:
        # реализуемая в ней функция, аргументы.
        self.structure: dict[str, tuple[str | int, ...]] = {}
        # Словарь, в котором каждой вершине сопосотовляется
        # её значение.
        self.values: dict[str, int] = {}
        # Словарь, где каждой вершине сопоставляется
        # её вектор значений на тестируемых наборах
        self.vertex_classes: dict[str, list[int]] = {}

    # Функция, задающая значения вершинам,
    # помеченным входами, в соответствии с заданным набором
    def set_input_values(self, values: list[int]) -> None:
        for i, input in enumerate(self.inputs):
            self.values[input] = values[i]

    # Функция, очищающая значения всех вершин,
    # кроме вершин, помеченных константами 0 и 1
    def clear_vertex_values(self) -> None:
        self.values = {
            "const0": 0,
            "const1": 1,
        }

    # Прогон одного набора. Функция устанавливает значения всех вершин
    # поддерева графа с корнем в cur_vert
    def fill_value(self, cur_vert: str) -> int:
        # Рассматривается случай, когда в текущей вершине
        # уже установлено значение
        if cur_vert in self.values:
            return self.values[cur_vert]

        vertex_info = self.structure[cur_vert]
        children: list[int] = []
        for i in range(1, len(vertex_info), 2):
            next_child = self.fill_value(str(vertex_info[i]))
            next_edge = vertex_info[i + 1]
            children += [1 ^ int(next_edge) ^ next_child]

        # Рассматривается случай, когда в вершине реализуется функция 'and'
        if vertex_info[0] == "and":
            self.values[cur_vert] = reduce((lambda child1, child2: child1 & child2), children)

        # Рассматривается случай, когда в вершине реализуется функция 'xor'
        elif vertex_info[0] == "xor":
            self.values[cur_vert] = reduce((lambda child1, child2: child1 ^ child2), children)

        # Рассматривается случай, когда в вершине реализуется функция 'h'
        elif vertex_info[0] == "h":
            self.values[cur_vert] = int(
                reduce((lambda child1, child2: child1 + child2), children) > (len(children) // 2)
            )

        else:
            raise ValueError(f"Unknown function: {vertex_info[0]}")

        self.vertex_classes[cur_vert].append(self.values[cur_vert])
        return self.values[cur_vert]

    # Функция для заполнения полей класса данными из файла json
    @classmethod
    def from_json(cls, file_name: str) -> InverseGraph:
        graph = cls()
        with open(file_name) as f:
            data = json.load(f)
            inputs = data["inputs"]
            outputs = data["outputs"]
            circuit = data["nodes"]
            graph._create_graph(circuit, inputs, outputs)
        return graph

    # Функция, заполняющая поля класса
    def _create_graph(self, circuit: dict[str, list[str | int]], inputs: list[str], outputs: list[str]) -> None:
        self.outputs = outputs
        self.inputs = sorted(inputs)

        # Заполняет вершины, помеченные константами 0 и 1
        self.structure["const0"] = ("const",)
        self.structure["const1"] = ("const",)
        self.values["const0"] = 0
        self.values["const1"] = 1

        for input_name in self.inputs:
            self.structure[input_name] = ("input",)

        for key in circuit.keys():
            vertex = circuit[key].copy()
            for i in range(1, len(vertex), 2):
                value = vertex[i]
                if value == 0:
                    vertex[i] = "const0"
                elif value == 1:
                    vertex[i] = "const1"

            self.structure[key] = tuple(vertex)
            self.vertex_classes[key] = []
