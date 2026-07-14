from typing import Union

from mk_eda.libs.common.logger import get_logger
from mk_eda.libs.graph.graph import AndNode, Child, InverterGraph, Node, RawGraph, XorNode, raise_error

logger = get_logger(__name__)


class XorAndInverterGraph(InverterGraph):
    def __init__(self):
        super().__init__()

    def f_and(self, left: Child, right: Child, name: Union[str, None] = None) -> str:
        logger.debug(f"Building node {left.name} & {right.name}")

        for child_name in [left.name, right.name]:
            if not self._exists(child_name):
                raise_error(f"Invalid node {child_name}")

        new_node = AndNode(left.name, left.sign, right.name, right.sign)

        return self.add_node(new_node, name)

    def f_xor(self, left: Child, right: Child, name: Union[str, None] = None) -> str:
        logger.debug(f"Building node {left.name} xor {right.name}")

        for child_name in [left.name, right.name]:
            if not self._exists(child_name):
                raise_error(f"Invalid node {child_name}")

        new_node = XorNode(left.name, left.sign, right.name, right.sign)

        return self.add_node(new_node, name)

    def add_node(self, node: Node, name: Union[str, None] = None) -> str:
        if node.function not in ["and", "xor"]:
            raise_error(f"Invalid vertex function '{node.function}'")
        return super().add_node(node, name)

    def _from_raw(self, graph: RawGraph) -> None:
        nodes = graph["nodes"]
        functions = {v[0] for v in nodes.values()}
        if not (functions <= {"and", "xor"}):
            raise_error("Invalid function set for XorAndInverterGraph")
        super()._from_raw(graph)
