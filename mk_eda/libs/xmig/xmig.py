from typing import Union

from mk_eda.libs.common.logger import get_logger
from mk_eda.libs.graph.graph import Child, InverterGraph, MajorityNode, Node, RawGraph, XorNode, raise_error

logger = get_logger(__name__)


class XorMajorityInverterGraph(InverterGraph):
    def __init__(self):
        super().__init__()

    def f_xor(self, left: Child, right: Child, name: Union[str, None] = None) -> str:
        logger.debug(f"Building node {left.name} ^ {right.name}")

        for child_name in [left.name, right.name]:
            if not self._exists(child_name):
                raise_error(f"Invalid node {child_name}")

        new_node = XorNode(left.name, left.sign, right.name, right.sign)

        return self.add_node(new_node, name)

    def f_majority(self, first: Child, second: Child, third: Child, name: Union[str, None] = None) -> str:
        logger.debug(f"Building node {first.name} & {second.name} & {third.name}")

        for child_name in [first.name, second.name, third.name]:
            if not self._exists(child_name):
                raise_error(f"Invalid node {child_name}")

        new_node = MajorityNode(first.name, first.sign, second.name, second.sign, third.name, third.sign)

        return self.add_node(new_node, name)

    def graph_statistics(self) -> dict[str, int]:
        xor_count = sum(1 for node in self._nodes.values() if node.function == "xor")
        majority_count = sum(1 for node in self._nodes.values() if node.function == "majority")
        total_count = len(self._nodes)

        stats = {
            "total_nodes": total_count,
            "xor_nodes": xor_count,
            "majority_nodes": majority_count,
        }
        logger.debug(f"Graph statistics: {stats}")

        return stats

    def add_node(self, node: Node, name: Union[str, None] = None) -> str:
        if node.function not in ["xor", "majority"]:
            raise_error(
                f"Invalid node function '{node.function}': only 'xor' and 'majority' functions"
                "are allowed for XorMajorityInverterGraph"
            )

        return super().add_node(node, name)

    def _from_raw(self, graph: RawGraph) -> None:
        nodes = graph["nodes"]
        functions = {v[0] for v in nodes.values()}

        if not (functions <= {"xor", "majority"}):
            error_message = (
                "Invalid function set: only 'xor' and 'majority' functions are allowed for XorMajorityInverterGraph"
            )
            logger.error(error_message)
            raise ValueError(error_message)

        super()._from_raw(graph)
