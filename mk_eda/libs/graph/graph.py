from __future__ import annotations

import json
from typing import TypedDict, Union

from pyeda.boolalg.expr import exprvar  # type: ignore
from typing_extensions import Self

from mk_eda.libs.common.functions import FUNCTIONS, BooleanFunction
from mk_eda.libs.common.logger import get_logger

logger = get_logger(__name__)


def raise_error(error_message: str) -> None:
    logger.error(error_message)
    raise KeyError(error_message)


RawPorts = list[str]
RawNode = list[Union[str, int]]
RawNodes = dict[str, RawNode]


class RawGraph(TypedDict):
    inputs: RawPorts
    outputs: RawPorts
    nodes: RawNodes


class Child:
    def __init__(self, name: str, sign: bool):
        self.name: str = name
        self.sign: bool = sign

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Child):
            return NotImplemented
        return self.name == other.name and self.sign == other.sign

    def __hash__(self) -> int:
        return hash((self.name, self.sign))


class Node:
    def __init__(self, function: str, children_list: list[str | int]):
        logger.debug(f"Creating new node {function}")
        self.function: str = function
        self.children: tuple[Child, ...] = Node.children_from_raw(children_list)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Node):
            return NotImplemented
        return self.function == other.function and self.children == other.children

    def __hash__(self) -> int:
        return hash((self.function, self.children))

    def __repr__(self) -> str:
        return ", ".join(map(str, self.to_raw()))

    def to_raw(self) -> RawNode:
        logger.debug("Making raw node from pure")
        children_list: list[str | int] = []
        for child in self.children:
            children_list += [child.name, int(child.sign)]
        return [self.function] + children_list

    @staticmethod
    def children_from_raw(raw_children: list[str | int]) -> tuple[Child, ...]:
        n_children = len(raw_children) // 2
        return tuple(Child(str(raw_children[2 * i]), bool(raw_children[2 * i + 1])) for i in range(n_children))


# в будущих ветках унаследовать NotNode от Node для превращения
# класса InverterGraph по смыслу в полноценный BooleanCircuit?
class NotNode:
    def __init__(self, negated_node: str):
        self.negated_node = negated_node

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NotNode):
            return NotImplemented
        return self.negated_node == other.negated_node

    def __str__(self) -> str:
        return self.negated_node


class TwoInputNode(Node):
    def __init__(self, function: str, left_name: str, left_sign: bool, right_name: str, right_sign: bool):
        super().__init__(function, [left_name, left_sign, right_name, right_sign])

    @property
    def left(self) -> Child:
        return self.children[0]

    @property
    def right(self) -> Child:
        return self.children[1]


class ThreeInputNode(Node):
    def __init__(
        self,
        function: str,
        first_name: str,
        first_sign: bool,
        second_name: str,
        second_sign: bool,
        third_name: str,
        third_sign: bool,
    ):
        super().__init__(function, [first_name, first_sign, second_name, second_sign, third_name, third_sign])

    @property
    def first(self) -> Child:
        return self.children[0]

    @property
    def second(self) -> Child:
        return self.children[1]

    @property
    def third(self) -> Child:
        return self.children[2]


class AndNode(TwoInputNode):
    def __init__(self, left_name: str, left_sign: bool, right_name: str, right_sign: bool):
        super().__init__("and", left_name, left_sign, right_name, right_sign)


class OrNode(TwoInputNode):
    def __init__(self, left_name: str, left_sign: bool, right_name: str, right_sign: bool):
        super().__init__("or", left_name, left_sign, right_name, right_sign)


class XorNode(TwoInputNode):
    def __init__(self, left_name: str, left_sign: bool, right_name: str, right_sign: bool):
        super().__init__("xor", left_name, left_sign, right_name, right_sign)


class ImpliesNode(TwoInputNode):
    def __init__(self, left_name: str, left_sign: bool, right_name: str, right_sign: bool):
        super().__init__("implies", left_name, left_sign, right_name, right_sign)


class MajorityNode(ThreeInputNode):
    def __init__(
        self, first_name: str, first_sign: bool, second_name: str, second_sign: bool, third_name: str, third_sign: bool
    ):
        super().__init__("majority", first_name, first_sign, second_name, second_sign, third_name, third_sign)


class NodeFactory:
    TWO_INPUT_NODES: dict[str, type[AndNode | OrNode | XorNode | ImpliesNode]] = {
        "and": AndNode,
        "or": OrNode,
        "xor": XorNode,
        "implies": ImpliesNode,
    }
    THREE_INPUT_NODES: dict[str, type[MajorityNode]] = {
        "majority": MajorityNode,
    }

    @classmethod
    def create(cls, raw_node: RawNode) -> Node:
        function = str(raw_node[0])
        if node_cls := cls.TWO_INPUT_NODES.get(function):
            return node_cls(str(raw_node[1]), bool(raw_node[2]), str(raw_node[3]), bool(raw_node[4]))
        if node_cls := cls.THREE_INPUT_NODES.get(function):
            return node_cls(
                str(raw_node[1]),
                bool(raw_node[2]),
                str(raw_node[3]),
                bool(raw_node[4]),
                str(raw_node[5]),
                bool(raw_node[6]),
            )
        return Node(function, raw_node[1:])


Nodes = dict[str, Node]


def nodes_from_raw(raw_nodes: RawNodes) -> Nodes:
    logger.debug("Making pure nodes from raw")
    return {name: NodeFactory.create(raw_node) for name, raw_node in raw_nodes.items()}


def nodes_to_raw(pure_nodes: Nodes) -> RawNodes:
    logger.debug("Making raw node from pure")
    return {name: pure_node.to_raw() for name, pure_node in pure_nodes.items()}


Ports = list[str]


class InverterGraph:
    def __init__(self):
        logger.debug("Creating new InverterGraph object")
        self.inputs: Ports = []
        self.outputs: Ports = []
        self._nodes: Nodes = {}
        self._new_node_num: int = 1
        self._cache: dict[str, BooleanFunction] = {}

    @property
    def nodes(self) -> Nodes:
        return self._nodes

    def set_nodes(self, new_nodes: Nodes) -> None:
        logger.debug("Setting new nodes")
        self._nodes = new_nodes

    def __getitem__(self, output: str) -> BooleanFunction:
        if output not in self.outputs:
            raise_error(f"Output {output} is not found")
        return self.construct_formula(output)

    # пересмотреть логику if-elif-else
    def add_node(self, node: Node, name: str | None = None) -> str:
        if name is None:
            name = self._generate_name()
        elif name in self.inputs or name in ["0", "1"]:
            raise_error(f"Node {name} already exists as an input or a constant")
        if name in self._nodes:
            logger.error(f"Node {name} already exists")
        else:
            self._nodes[name] = node
            logger.debug(f"Added node {name}")
        return name

    def add_input(self, name: str) -> None:
        if name in self.inputs:
            raise_error(f"Input {name} already exists")
        self.inputs.append(name)

    def add_output(self, name: str) -> None:
        if name in self.outputs:
            raise_error(f"Output {name} already exists")
        self.outputs.append(name)

    def delete_node(self, name: str) -> None:
        if name not in self._nodes:
            raise_error(f"Node {name} is not found")
        logger.info(f"Deleting node {name}")
        self._nodes.pop(name)

    def delete_nodes(self, node_names: list[str]) -> None:
        for key in node_names:
            self.delete_node(key)

    def delete_input(self, name: str) -> None:
        if name not in self.inputs:
            raise_error(f"Input {name} is not found")
        self.inputs.remove(name)

    def delete_output(self, name: str) -> None:
        if name not in self.outputs:
            raise_error(f"Output {name} is not found")
        self.outputs.remove(name)

    def subgraph(self, root: str) -> InverterGraph:
        logger.debug(f"Building subgraph with output {root}")

        if not self._exists(root):
            logger.error(f"Invalid node {root}")
            raise KeyError(f"Invalid node {root}")

        subgraph = InverterGraph()
        for input_var in self.inputs:
            subgraph.add_input(input_var)

        stack: list[str] = [root]
        while len(stack) > 0:
            name = stack.pop()
            subgraph.add_node(self.nodes[name], name)
            for child in self.nodes[name].children:
                if child.name not in self.inputs:
                    stack.append(child.name)

        subgraph.add_output(root)
        return subgraph

    @classmethod
    def from_json(cls, file_name: str) -> Self:
        circuit = cls()
        circuit.load(file_name)
        return circuit

    def load(self, file_name: str, force_reload: bool = False) -> None:
        if self._nodes and not force_reload:
            print("Already loaded; to force reload use 'force_reload=True'")
            logger.info("Circuit is already loaded")
            return
        logger.info(f"Opening file '{file_name}'")
        with open(file_name) as file:
            logger.info(f"Loading from file {file_name}")
            graph = json.load(file)
        self._from_raw(graph)

    def dump(self, file_name: str) -> None:
        graph = self._to_raw()
        logger.info(f"Opening file '{file_name}'")
        with open(file_name, "w") as file:
            logger.info(f"Dumping to file '{file_name}'")
            json.dump(graph, file, indent=4)

    def cut(self, cut_list: list[str]) -> list[str]:
        logger.info("Cutting circuit")
        new_outputs: list[str] = []
        for vertex in cut_list:
            logger.debug(f"Cutting by vertex {vertex}")
            if vertex not in self._nodes:
                raise_error(f"Vertex to cut {vertex} not found")
            new_vertex = self._generate_name()
            self._nodes[new_vertex] = self._nodes.pop(vertex)
            new_outputs.append(new_vertex)
        for item in new_outputs:
            if item not in self.outputs:
                self.outputs.append(item)
        logger.debug(f"After cutting: inputs = {self.inputs}, outputs = {self.outputs}, nodes = {self._nodes}")
        cut_set = list(set(cut_list))
        for output in self.outputs:
            self._reset(output, cut_set)
        for item in cut_set:
            if item not in self.inputs:
                self.inputs.append(item)
        return new_outputs

    # после введения NotNode как подкласса Node переписать f_or в AIG
    # и здесь заменить всё это с dict на formula.restrict_values
    def evaluate(self, root: str, values: dict[str, bool]) -> bool:
        logger.info(f"Evaluating node {root} on input values {values}")
        evaluation_dict: dict[str, bool] = {"0": False, "1": True}
        for input_var in self.inputs:
            evaluation_dict[input_var] = values[input_var]
        for name, node in self._nodes.items():
            args_list: list[bool] = [(not child.sign) ^ evaluation_dict[child.name] for child in node.children]
            evaluation_dict[name] = bool(FUNCTIONS[node.function](*args_list))
        if root not in evaluation_dict:
            raise_error("Invalid node")
        return bool(evaluation_dict[root])

    def construct_formula(self, root: str) -> BooleanFunction:
        """Construct the boolean expression for the specified output."""
        if root not in self._cache:
            if root == "0":
                self._cache[root] = exprvar("0")
            elif root == "1":
                self._cache[root] = exprvar("1")
            elif root in self.inputs:
                self._cache[root] = exprvar(root)  # type: ignore
            elif root in self._nodes:
                node = self._nodes[root]
                subformulas: list[BooleanFunction] = [
                    (not child.sign) ^ self.construct_formula(child.name) for child in node.children
                ]
                self._cache[root] = FUNCTIONS[node.function](*subformulas)
            else:
                raise_error(f"Unknown node {root}")
        return self._cache[root]

    def print(self) -> None:
        print("inputs:", self.inputs)
        print("outputs:", self.outputs)
        print("nodes:", nodes_to_raw(self._nodes))

    def _from_raw(self, graph: RawGraph) -> None:
        logger.debug("Compose graph from inputs, outputs and nodes")
        InverterGraph._check_keys(graph)
        inputs = graph["inputs"]
        outputs = graph["outputs"]
        InverterGraph._check_sets(inputs, outputs, list(graph["nodes"].keys()))
        self.inputs = inputs
        self.outputs = outputs
        self._nodes = nodes_from_raw(graph["nodes"])
        self._new_node_num = 1

    @staticmethod
    def _check_keys(graph: RawGraph) -> None:
        if graph.keys() != {"inputs", "outputs", "nodes"}:
            raise_error("Keys are not equal to {'inputs', 'outputs', 'nodes'}")

    @staticmethod
    def _check_sets(inputs: Ports, outputs: Ports, nodes_names: list[str]) -> None:
        if not InverterGraph._isdisjoint_list(inputs, nodes_names):
            raise_error("Inputs cannot be nodes too")
        avaible_names = inputs + ["0", "1"] + nodes_names
        if not all(output in avaible_names for output in outputs):
            raise_error("Outputs should be a subset of nodes and inputs")

    @staticmethod
    def _isdisjoint_list(lst1: Ports, lst2: Ports) -> bool:
        return not any(item in lst1 for item in lst2)

    def _to_raw(self) -> RawGraph:
        logger.debug("Make RawGraph from self.(inputs, outputs, nodes)")
        return {"inputs": list(self.inputs), "outputs": list(self.outputs), "nodes": nodes_to_raw(self._nodes)}

    def _reset(self, root: str, new_inputs: Ports) -> bool:
        logger.debug(f"Resetting node {root}")
        if root in self.inputs:
            return False
        elif root in new_inputs:
            return True
        elif root not in self._cache:
            return True
        else:
            need_reset = False
            for child in self._nodes[root].children:
                need_reset |= self._reset(child.name, new_inputs)
            if need_reset:
                self._cache.pop(root)
            return need_reset

    def _generate_name(self) -> str:
        logger.debug("Choosing name for new node")
        while f"y{self._new_node_num}" in self._nodes:
            self._new_node_num += 1
        return f"y{self._new_node_num}"

    def _exists(self, node: str) -> bool:
        return node in self.inputs or node in self._nodes or node in ["0", "1"]
