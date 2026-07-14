from typing import Union

from mk_eda.libs.common.logger import get_logger
from mk_eda.libs.graph.graph import AndNode, Child, InverterGraph, Node, RawGraph, raise_error

logger = get_logger(__name__)


class AndInverterGraph(InverterGraph):
    def __init__(self):
        super().__init__()

    @property
    def nodes(self) -> dict[str, AndNode]:  # type: ignore
        return self._nodes  # type: ignore

    def f_and(self, left: Child, right: Child, name: Union[str, None] = None) -> str:
        logger.debug(f"Building node {left} & {right}")

        for child_name in [left.name, right.name]:
            if not self._exists(child_name):
                logger.error(f"Invalid node {child_name}")
                raise KeyError(f"Invalid node {child_name}")

        res_node = AndNode(left.name, left.sign, right.name, right.sign)

        return self.add_node(res_node, name)

    def f_or(self, left: Child, right: Child, name: Union[str, None] = None) -> str:
        logger.debug(f"Building node ~({left} | {right})")

        not_or = self.f_and(self._f_not(left), self._f_not(right))
        return self.f_and(Child(not_or, False), Child("1", True), name)

    def f_xor(self, left: Child, right: Child, name: Union[str, None] = None) -> str:
        logger.debug(f"Building ~({left} ^ {right})")
        t1 = self.f_and(left, self._f_not(right))
        t2 = self.f_and(self._f_not(left), right)
        return self.f_or(Child(t1, True), Child(t2, True), name)

    def _f_not(self, node: Child) -> Child:
        return Child(node.name, not node.sign)

    def add_node(self, node: Node, name: Union[str, None] = None) -> str:
        if node.function != "and":
            raise_error(f"Invalid vertex function '{node.function}'")
        return super().add_node(node, name)

    def _from_raw(self, graph: RawGraph) -> None:
        nodes = graph["nodes"]
        functions = {v[0] for v in nodes.values()}
        if not (functions <= {"and"}):
            raise_error("Invalid function set for AndInverterGraph")
        super()._from_raw(graph)
