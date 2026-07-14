from __future__ import annotations

from mk_eda.libs.aig.aig import AndInverterGraph
from mk_eda.libs.common.logger import get_logger
from mk_eda.libs.graph.graph import Node

logger = get_logger(__name__)


class AIGRewriter:
    def __call__(self, aig: AndInverterGraph) -> AndInverterGraph:
        return self.rewrite(aig)

    def rewrite(self, aig: AndInverterGraph) -> AndInverterGraph:
        self.delete_identical(aig)
        self.change_to_null(aig)
        self.delete_equal_nodes(aig)
        self.delete_inverse_and_idempotent(aig)
        self.make_absorption(aig)
        return aig

    def delete_identical(self, aig: AndInverterGraph) -> None:
        to_delete: list[str] = []
        for node_name, node in aig.nodes.items():
            if node.right.name == "1" and node.right.sign or node.right.name == "0" and not node.right.sign:
                logger.debug(f"Deleting {node_name} indentical to {node.left.name}^{node.left.sign}")
                self._replace_all_instances_of_node(aig, node_name, node.left.name, not node.left.sign)
                to_delete.append(node_name)
            if node.left.name == "1" and node.left.sign or node.left.name == "0" and not node.left.sign:
                logger.debug(f"Deleting {node_name} indentical to {node.right.name}^{node.right.sign}")
                self._replace_all_instances_of_node(aig, node_name, node.right.name, not node.right.sign)
                to_delete.append(node_name)
        aig.delete_nodes(to_delete)

    def change_to_null(self, aig: AndInverterGraph) -> None:
        to_delete: list[str] = []
        for node_name, node in aig.nodes.items():
            if any(
                (
                    node.left.name == "0" and node.left.sign,
                    node.left.name == "1" and not node.left.sign,
                    node.right.name == "0" and node.right.sign,
                    node.right.name == "1" and not node.right.sign,
                )
            ):
                self._replace_all_instances_of_node(aig, node_name, "0")
                to_delete.append(node_name)
        aig.delete_nodes(to_delete)

    def delete_equal_nodes(self, aig: AndInverterGraph) -> None:
        to_delete: list[str] = []
        seen_nodes: dict[Node, str] = {}
        for node_name, node in aig.nodes.items():
            if node not in seen_nodes:
                seen_nodes[node] = node_name
            else:
                to_delete.append(node_name)
                logger.info(f"found equal nodes: {seen_nodes[node]} and {node_name}")
                self._replace_all_instances_of_node(aig, node_name, seen_nodes[node])
        aig.delete_nodes(to_delete)

    def delete_inverse_and_idempotent(self, aig: AndInverterGraph) -> None:
        to_delete: list[str] = []
        for node_name, node in aig.nodes.items():
            if node.left.name == node.right.name:
                if node.left.sign != node.right.sign:
                    self._replace_all_instances_of_node(aig, node_name, "0")
                else:
                    self._replace_all_instances_of_node(aig, node_name, node.right.name, not node.right.sign)
                to_delete.append(node_name)
        aig.delete_nodes(to_delete)

    def make_absorption(self, aig: AndInverterGraph) -> None:
        to_delete: list[str] = []
        self.delete_identical(aig)
        for node_name, node in aig.nodes.items():
            child1, sign1 = node.left.name, node.left.sign
            child2, sign2 = node.right.name, node.right.sign
            if self._check_absorption(aig, child1, child2, sign2) and not sign1:
                logger.debug(f"Absorbing {node_name} by {child2}")
                self._replace_all_instances_of_node(aig, node_name, child2, not sign2)
                to_delete.append(node_name)
            elif self._check_absorption(aig, child2, child1, sign1) and not sign2:
                logger.debug(f"Absorbing {node_name} by {child1}")
                self._replace_all_instances_of_node(aig, node_name, child1, not sign1)
                to_delete.append(node_name)
        aig.delete_nodes(to_delete)

    def _replace_all_instances_of_node(
        self, aig: AndInverterGraph, old_node: str, new_node: str, inversion: bool = False
    ) -> None:
        for node in aig.nodes.values():
            if node.left.name == old_node:
                node.left.name = new_node
                node.left.sign ^= inversion
            if node.right.name == old_node:
                node.right.name = new_node
                node.right.sign ^= inversion

    def _check_absorption(self, aig: AndInverterGraph, child1: str, x: str, sign: bool) -> bool:
        if child1 not in aig.nodes:
            return False
        return (
            aig.nodes[child1].left.name == x
            and aig.nodes[child1].left.sign != sign
            or aig.nodes[child1].right.name == x
            and aig.nodes[child1].right.sign != sign
        )
