from typing import Union

from mk_eda.libs.graph.graph import Node
from mk_eda.libs.xaig.xaig import XorAndInverterGraph


class XAIGComplexityOptimizer:
    def __call__(self, xaig: XorAndInverterGraph, iterations: int = 1) -> XorAndInverterGraph:
        return self.optimize(xaig, iterations)

    def optimize(self, xaig: XorAndInverterGraph, iterations: int = 1) -> XorAndInverterGraph:
        """Оптимизация XAIG по сложности на основе классических эквивалентных преобразований."""
        for _ in range(iterations):
            outputs = xaig.outputs.copy()
            for output in outputs:
                if not self._optimize_output(xaig, output):
                    self._recursively_optimize(xaig, output)

            connected = [child for node in xaig.nodes.values() for child in (node.to_raw()[1], node.to_raw()[3])]
            rm_list = [
                name
                for name in xaig.nodes.keys()
                if name not in xaig.inputs and name not in xaig.outputs and name not in connected
            ]
            xaig.delete_nodes(rm_list)

        return xaig

    def _recursively_optimize(self, xaig: XorAndInverterGraph, name: str) -> tuple[int, int, int]:
        """Рекурсивная оптимизация графа XAIG."""
        if name in xaig.inputs or name in ["0", "1"]:
            return 0, -1, -1

        root = xaig.nodes[name]

        left, left_left, left_right = self._recursively_optimize(xaig, root.children[0].name)
        right, right_left, right_right = self._recursively_optimize(xaig, root.children[1].name)

        return self._optimize_children_connections(
            xaig, [left, left_left, left_right, right, right_left, right_right], name
        )

    def _optimize_children_connections(
        self, xaig: XorAndInverterGraph, children_info: list[int], name: str
    ) -> tuple[int, int, int]:
        """Удаляет узлы, которые подключены к одному и тому же узлу с обеих сторон."""
        root = xaig.nodes[name]
        children_info = [children_info[0], children_info[3]]
        children_list: list[Union[int, str]] = []

        for i, child in enumerate(root.children):
            if children_info[i] < 1:  # это вход
                children_list.extend([child.name, int(child.sign)])
                continue

            node = xaig.nodes[child.name]
            if node.children[0].name != node.children[1].name:
                children_list.extend([child.name, int(child.sign)])
                continue

            if node.function == "and":
                if node.children[0].sign != node.children[1].sign:
                    children_list.extend(["0", 1])
                    children_info[i] = 0
                else:
                    children_list.extend([node.children[0].name, node.children[0].sign])
                    children_info[i] -= 1

            if node.function == "xor":
                children_list.extend([f"{int(node.children[0].sign != node.children[1].sign)}", 1])
                children_info[i] = 0

        new_root = Node(root.function, children_list)
        xaig.delete_node(name)
        xaig.add_node(new_root, name)

        return max(children_info) + 1, children_info[0], children_info[1]

    def _optimize_output(self, xaig: XorAndInverterGraph, output: str) -> bool:
        """Оптимизирует выходной узел, пытаясь удалить ненужные узлы."""
        if output in xaig.inputs or output in ["0", "1"]:
            return False

        node = xaig.nodes[output]

        if node.function == "and":
            for i in range(2):
                if node.children[i].name in ["0", "1"]:
                    value = (node.children[i].name == "1") == node.children[i].sign
                    if not value:
                        self._replace_output(xaig, output, "0")
                        return True
                    elif node.children[1 - i].sign:
                        self._replace_output(xaig, output, node.children[1 - i].name)
                        return True
            if node.children[0].name == node.children[1].name:
                if node.children[0].sign != node.children[1].sign:
                    self._replace_output(xaig, output, "0")
                    return True
                elif node.children[0].sign:
                    self._replace_output(xaig, output, node.children[0].name)
                    return True

        if node.function == "xor":
            for i in range(2):
                if node.children[i].name in ["0", "1"]:
                    value = (node.children[i].name == "1") == node.children[i].sign
                    if node.children[1 - i].sign != value:
                        self._replace_output(xaig, output, node.children[1 - i].name)
                        return True
            if node.children[0].name == node.children[1].name:
                if node.children[0].sign != node.children[1].sign:
                    self._replace_output(xaig, output, "1")
                    return True
                else:
                    self._replace_output(xaig, output, "0")
                    return True
        return False

    def _replace_output(self, xaig: XorAndInverterGraph, output: str, new_output: str) -> None:
        """Заменяет выходной узел новым узлом."""
        xaig.delete_output(output)
        if new_output not in xaig.outputs:
            xaig.add_output(new_output)
