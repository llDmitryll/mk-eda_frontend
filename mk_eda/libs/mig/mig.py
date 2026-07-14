from typing import Union

from mk_eda.libs.common.logger import get_logger
from mk_eda.libs.graph.graph import Child, InverterGraph, MajorityNode, Node, RawGraph

logger = get_logger(__name__)


class MajorityInverterGraph(InverterGraph):
    def __init__(self):
        super().__init__()

    def f_maj(self, first: Child, second: Child, third: Child, name: Union[str, None] = None) -> str:
        logger.debug(f"Building node {first.name} & {second.name} & {third.name}")

        for wrong_child in [first.name, second.name, third.name]:
            if not self._exists(wrong_child):
                logger.error(f"Invalid node wrong child {wrong_child}")
                raise KeyError(f"Invalid node wrong child {wrong_child}")

        new_node = MajorityNode(first.name, first.sign, second.name, second.sign, third.name, third.sign)

        return self.add_node(new_node, name)

    def add_node(self, node: Node, name: Union[str, None] = None) -> str:
        if node.function != "majority":
            logger.error(f"Invalid vertex function '{node.function}'")
            raise KeyError(f"Invalid vertex function '{node.function}'")
        return super().add_node(node, name)

    def _from_raw(self, graph: RawGraph) -> None:
        nodes = graph["nodes"]
        functions = {v[0] for v in nodes.values()}
        if not all(func == "majority" for func in functions):
            logger.error("Invalid function set for MajorityInverterGraph")
            raise KeyError("Invalid function set for MajorityInverterGraph")
        super()._from_raw(graph)
