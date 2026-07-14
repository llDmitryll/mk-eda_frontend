from mk_eda.libs.aig.aig import AndInverterGraph
from mk_eda.libs.graph.graph import Child, Node


class AIGComplexityOptimizer:
    def __call__(self, graph: AndInverterGraph, n: int = 1) -> AndInverterGraph:
        return self.optimize(graph, n)

    def optimize(self, graph: AndInverterGraph, n: int = 1) -> AndInverterGraph:
        for _ in range(n):
            self._optimize_zero_edges(graph)
            self._optimize_one_edges(graph)
            self._normalize_graph(graph)
            self._remove_unused_nodes(graph)
        return graph

    def _remove_unused_nodes(self, graph: AndInverterGraph) -> None:
        used_nodes: set[str] = set()
        for output in graph.outputs:
            self._traverse(graph, output, used_nodes)

        graph.set_nodes({name: node for name, node in graph.nodes.items() if name in used_nodes})

    def _normalize_graph(self, graph: AndInverterGraph) -> None:
        node_hash_map: dict[tuple[str, tuple[tuple[str, bool], ...]], str] = {}
        new_nodes: dict[str, Node] = {}

        for node_name, node_data in graph.nodes.items():
            node_hash = (node_data.function, tuple((child.name, child.sign) for child in node_data.children))

            if node_hash not in node_hash_map:
                node_hash_map[node_hash] = node_name
                new_nodes[node_name] = node_data
            else:
                duplicate_name = node_hash_map[node_hash]

                if node_name in graph.outputs:
                    node_hash_map[node_hash] = node_name
                    new_nodes[node_name] = node_data
                else:
                    for _, n_data in graph.nodes.items():
                        for child in n_data.children:
                            if child.name == node_name:
                                child.name = duplicate_name

        graph.set_nodes(new_nodes)

    def _optimize_one_edges(self, graph: AndInverterGraph) -> None:
        nodes_to_remove: list[str] = []

        for node_name, node in graph.nodes.items():
            left, right = node.children[0], node.children[1]
            if left.name == "1" and left.sign or left.name == "0" and not left.sign:
                self._replace_node_references(graph, node_name, right.name, True)
                nodes_to_remove.append(str(node_name))
            elif right.name == "1" and right.sign or right.name == "0" and not right.sign:
                self._replace_node_references(graph, node_name, left.name, True)
                nodes_to_remove.append(str(node_name))
            elif right.name == left.name and right.sign == left.sign:
                self._replace_node_references(graph, node_name, left.name, True)
                nodes_to_remove.append(str(node_name))

        graph.delete_nodes(nodes_to_remove)

    def _optimize_zero_edges(self, graph: AndInverterGraph) -> None:
        nodes_to_remove: list[str] = []

        for node_name, node in graph.nodes.items():
            left, right = node.children[0], node.children[1]
            if left.name == "1" and not left.sign or left.name == "0" and left.sign:
                self._replace_node_references(graph, node_name, "0", False)
                nodes_to_remove.append(str(node_name))
            elif right.name == "1" and not right.sign or right.name == "0" and right.sign:
                self._replace_node_references(graph, node_name, "0", False)
                nodes_to_remove.append(str(node_name))
            elif right.name == left.name and right.sign != left.sign:
                self._replace_node_references(graph, node_name, "0", False)
                nodes_to_remove.append(str(node_name))

        graph.delete_nodes(nodes_to_remove)

        if not graph.nodes:
            graph.outputs.clear()
            graph.add_output("0")
        else:
            for node_name in nodes_to_remove:
                if node_name in graph.outputs:
                    graph.outputs.remove(node_name)
        if not graph.outputs:
            graph.add_output("0")

    def _replace_node_references(self, graph: AndInverterGraph, old_node: str, new_node: str, param: bool) -> None:
        if param:  # True - optimization x1 & 1
            if old_node in graph.outputs:
                graph.outputs[graph.outputs.index(old_node)] = new_node

        for node_name, node in graph.nodes.items():
            updated_children: list[Child] = []
            for child in node.children:
                if child.name == old_node:
                    updated_children.append(Child(new_node, child.sign))
                else:
                    updated_children.append(child)
            graph.nodes[node_name].children = tuple(updated_children)

    def _traverse(self, graph: AndInverterGraph, node_name: str, used_nodes: set[str]):
        if node_name in ["0", "1"]:
            return
        if node_name in used_nodes:
            return
        if node_name in graph.inputs:
            return
        used_nodes.add(node_name)
        node = graph.nodes[node_name]
        for child in node.children:
            self._traverse(graph, child.name, used_nodes)
