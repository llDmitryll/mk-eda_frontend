from itertools import chain
from typing import Union

from mk_eda.libs.graph.graph import Node
from mk_eda.libs.xaig.xaig import XorAndInverterGraph


class XAIGDepthOptimizer:
    def __call__(self, xaig: XorAndInverterGraph, iterations: int = 1) -> XorAndInverterGraph:
        return self.optimize(xaig, iterations)

    def optimize(self, xaig: XorAndInverterGraph, iterations: int = 1) -> XorAndInverterGraph:
        for _ in range(iterations):
            blocks = xaig.outputs.copy()
            for output in blocks:
                if not self._optimize_output(xaig, output):  # first try to remove output
                    self._recursively_optimize(xaig, output)
            # remove hunging nodes
            rm_list: list[str] = []
            # list of nodes, connected to other nodes
            node_inputs_pairs = [[node.to_raw()[1], node.to_raw()[3]] for node in xaig.nodes.values()]
            connected = list(chain.from_iterable(node_inputs_pairs))
            for name in xaig.nodes.keys():
                if name in xaig.inputs or name in xaig.outputs:  # node is in use
                    continue
                if name not in connected:  # node connected to nothing
                    rm_list.append(name)
            xaig.delete_nodes(rm_list)

        return xaig

    def _recursively_optimize(self, xaig: XorAndInverterGraph, name: str) -> tuple[int, int, int]:
        # depth first search in xaig, returns depth of tree, left subtree, right subtree
        # possibly, leaves hunging nodes (to not breake other inputs)

        if name in xaig.inputs or name in ["0", "1"]:  # input
            return (0, -1, -1)

        root = xaig.nodes[name]

        # calculate parameters for subtrees
        left, left_left, left_right = self._recursively_optimize(xaig, root.children[0].name)
        right, right_left, right_right = self._recursively_optimize(xaig, root.children[1].name)

        main_subtree = int(left < right)  # number of subtree with bigger depth

        if abs(left - right) >= 2:  # subtrees arn't balanced
            if root.children[main_subtree].sign:  # children arn't connected with negation
                subtree = xaig.nodes[root.children[main_subtree].name]
                if root.function == subtree.function:  # children arn't connected with different operation
                    # optimization by reconnecting children
                    return self._recombine(xaig, [left, left_left, left_right, right, right_left, right_right], name)

        # optimization is not possible
        return self._replace_trivial(xaig, [left, left_left, left_right, right, right_left, right_right], name)

    def _optimize_output(self, xaig: XorAndInverterGraph, name: str) -> bool:
        # replase usless node in output, leaves it in graph, possibly hanging
        if name in xaig.inputs or name in ["0", "1"]:
            return False

        node = xaig.nodes[name]

        if node.function == "and":
            for i in range(2):
                if node.children[i].name == "0" or node.children[i].name == "1":
                    # value on node input
                    value = (node.children[i].name == "1") == node.children[i].sign
                    if not value:
                        self._replace_output(xaig, name, "0")
                        return True
                    elif node.children[1 - i].sign:  # multiply another node by 1
                        self._replace_output(xaig, name, node.children[1 - i].name)
                        return True
            if node.children[0].name == node.children[1].name:
                if node.children[0].sign != node.children[1].sign:
                    self._replace_output(xaig, name, "0")
                    return True
                elif node.children[0].sign:
                    self._replace_output(xaig, name, node.children[0].name)
                    return True

        if node.function == "xor":
            for i in range(2):
                if node.children[i].name == "0" or node.children[i].name == "1":
                    # value on node input
                    value = (node.children[i].name == "1") == node.children[i].sign
                    if node.children[1 - i].sign != value:
                        self._replace_output(xaig, name, node.children[1 - i].name)
                        return True
            if node.children[0].name == node.children[1].name:
                if node.children[0].sign != node.children[1].sign:
                    self._replace_output(xaig, name, "1")
                    return True
                else:
                    self._replace_output(xaig, name, "0")
                    return True
        return False

    def _recombine(self, xaig: XorAndInverterGraph, children_info: list[int], name: str) -> tuple[int, int, int]:
        # recombines subtrees in better way
        root = xaig.nodes[name]
        left, left_left, left_right, right, right_left, right_right = children_info

        main_subtree = int(left < right)  # number of subtree with bigger depth
        side_subtree = 1 - main_subtree
        side_subtree_depth, main_subtree_depth = sorted([left, right])

        children = (left_left, left_right) if left > right else (right_left, right_right)
        main_child = int(children[0] < children[1])  # number of subtree's child with bigger depth
        side_child = 1 - main_child
        side_child_depth = min(children)

        subtree = xaig.nodes[root.children[main_subtree].name]

        # optimization is possible
        intermediate_node = Node(
            root.function,
            [
                subtree.children[side_child].name,
                subtree.children[side_child].sign,
                root.children[side_subtree].name,
                root.children[side_subtree].sign,
            ],
        )
        intermediate_name = xaig.add_node(intermediate_node)

        new_root = Node(
            root.function,
            [subtree.children[main_child].name, subtree.children[main_child].sign, intermediate_name, True],
        )
        xaig.delete_node(name)
        xaig.add_node(new_root, name)

        return (main_subtree_depth, main_subtree_depth - 1, max(side_subtree_depth, side_child_depth) + 1)

    # TODO: use extend
    def _replace_trivial(self, xaig: XorAndInverterGraph, children_info: list[int], name: str) -> tuple[int, int, int]:
        # removes node, connected to one node with both sides
        root = xaig.nodes[name]
        children_info = [children_info[0], children_info[3]]
        children_list: list[Union[int, str]] = []
        for i, child in enumerate(root.children):
            if children_info[i] < 1:  # it's input
                children_list.append(child.name)
                children_list.append(int(child.sign))
                continue

            node = xaig.nodes[child.name]
            if node.children[0].name != node.children[1].name:  # different children
                children_list.append(child.name)
                children_list.append(int(child.sign))
                continue

            if node.function == "and":
                if node.children[0].sign != node.children[1].sign:
                    children_list.append("0")
                    children_list.append(1)
                    # update information for return
                    children_info[i] = 0
                else:  # same sign
                    children_list.append(node.children[0].name)
                    children_list.append(node.children[0].sign)
                    # update information for return
                    children_info[i] -= 1
            else:  # xor
                # always constant
                children_list.append(f"{int(node.children[0].sign != node.children[1].sign)}")
                children_list.append(1)
                # update information for return
                children_info[i] = 0

        new_root = Node(root.function, children_list)
        xaig.delete_node(name)
        xaig.add_node(new_root, name)

        return (max(children_info) + 1, children_info[0], children_info[1])

    def _replace_output(self, xaig: XorAndInverterGraph, name: str, new_name: str) -> None:
        xaig.delete_output(name)
        if new_name not in xaig.outputs:
            xaig.add_output(new_name)
