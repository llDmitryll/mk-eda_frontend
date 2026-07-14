import copy

from mk_eda.libs.graph.graph import InverterGraph, Node


def child_partition(
    vertex: str,
    sub_graph: InverterGraph,
    graph: InverterGraph,
    used: dict[str, int],
    depths: dict[str, int],
    delete: bool,
):
    children_depths: list[int] = []
    for child in graph.nodes[vertex].children:
        if child.name in graph.outputs:
            sub_graph.add_output(child.name)
            graph.outputs.remove(child.name)

        if child.name in graph.inputs:
            if child.name not in sub_graph.inputs:
                sub_graph.add_input(child.name)
            if used[child.name] == 1 and delete:
                graph.delete_input(child.name)
                used.pop(child.name)
                depths.pop(child.name, None)
            else:
                if delete:
                    used[child.name] -= 1
        else:  # child is node
            sub_graph.add_node(graph.nodes[child.name], child.name)
            if used[child.name] == 1 and delete:
                child_partition(child.name, sub_graph, graph, used, depths, delete)
                graph.delete_node(child.name)
                used.pop(child.name)
                depths.pop(child.name, None)
            else:
                child_partition(child.name, sub_graph, graph, used, depths, False)
                if delete:
                    used[child.name] -= 1
        children_depths.append(depths.get(child.name, 0))
    depths[vertex] = max(children_depths) + 1


def depth_recurs(node_out: str, node: Node, graph: InverterGraph, depths: dict[str, int]) -> int:
    if depths.get(node_out, None) is None:
        children_depth: list[int] = []
        for child in node.children:
            child_depth = depths.get(child.name, None)
            if child_depth is not None:
                children_depth.append(depths[child.name])
            else:
                children_depth.append(depth_recurs(child.name, graph.nodes[child.name], graph, depths))
        depths[node_out] = max(children_depth) + 1
        return depths[node_out]
    return 0


def depth_partitioner(graph: InverterGraph, depth: int):
    graph = copy.deepcopy(graph)
    depths: dict[str, int] = {}
    used: dict[str, int] = {}
    for input in graph.inputs:
        depths[input] = 0
    for node_out, node in graph.nodes.items():
        depth_recurs(node_out, node, graph, depths)
        for child in node.children:
            used[child.name] = used.get(child.name, 0) + 1

    fragmentation: list[InverterGraph] = []
    while max(depths.values()) > depth:
        depth_items = list(depths.items())
        for key, value in depth_items:
            if value == depth:
                sub_graph = InverterGraph()
                sub_graph.add_output(key)
                sub_graph.add_node(graph.nodes[key], key)

                child_partition(key, sub_graph, graph, used, depths, True)

                if key in graph.outputs and not used.get(key):
                    graph.outputs.remove(key)
                if used.get(key):
                    graph.add_input(key)
                graph.delete_node(key)
                fragmentation.append(sub_graph)
                depths.pop(key)
        for key, value in depth_items:
            if value > depth:
                children_depths: list[int] = []
                for child in graph.nodes[key].children:
                    children_depths.append(depths.get(child.name, 0))
                depths[key] = max(children_depths) + 1

    fragmentation.append(graph)
    return fragmentation
