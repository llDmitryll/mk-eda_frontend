import re
from collections.abc import Generator
from typing import TypedDict, Union

Nodes = dict[str, list[Union[str, int]]]


class AigDict(TypedDict):
    inputs: list[str]
    outputs: list[str]
    nodes: Nodes


class ReadFile:
    def __init__(self, file_name: str) -> None:
        self._file_name = file_name
        self._file = open(file_name, "rb")
        self._format = self._file.readline().decode().split()[0]
        if self._format not in ["aag", "aig"]:
            raise ValueError("Unknown file format")
        self._file.close()
        if self._format == "aag":
            self._file = open(file_name)
        else:
            self._sequence = self._get_aig()

    def _get_aag(self) -> list[int]:
        result = self._file.readline().split()
        if not result[0].isdigit():
            result = result[1:]
        return list(map(int, result))

    def _get_aig(self) -> Generator[list[int], None, None]:
        self._file.close()
        self._file = open(self._file_name, "rb")
        specifications = list(map(int, self._file.readline().split()[1:]))
        yield specifications
        _, inputs, latches, outputs, gates = specifications

        for i in range(1, inputs + 1):  # all variables are inputs
            yield [2 * i]

        index = 2 * (inputs)
        for _ in range(latches):
            index += 2
            yield [index, int(self._file.readline())]

        for _ in range(outputs):
            output = [int(self._file.readline())]
            yield output

        for _ in range(gates):
            index += 2
            deltas: list[int] = []
            for _ in range(2):
                x, i = [0, 0]
                byte = int.from_bytes(self._file.read(1), byteorder="big")
                while byte & 0x80:
                    x |= (byte & 0x7F) << (7 * i)
                    i += 1
                    byte = int.from_bytes(self._file.read(1), byteorder="big")
                x |= byte << (7 * i)
                deltas.append(x)
            yield [index, index - deltas[0], index - (deltas[0] + deltas[1])]

    def get(self) -> list[int]:
        if self._format == "aag":
            return self._get_aag()
        else:
            return next(self._sequence)


def resolve_gate(number: int, index: int, vertexes: dict[str, int]) -> str:
    # returns right name for output, coordinate it with outputs
    names = [key for key, value in vertexes.items() if value == index]
    name = f"y{number}"
    for s in names:
        if s[0] == "f":
            if name[0] == "f":  # node is in output list twice
                raise ValueError("Double output")
        name = s  # node is in output list so it's name starts with 'f'
    return name


def resolve_output(number: int, index: int, vertexes: dict[str, int]) -> tuple[str, int]:
    names = [key for key, value in vertexes.items() if value == index]
    if len(names) < 1:
        return (f"f{number}", index)
    if len(names) > 1:
        raise ValueError(f"Indefinite input {index}")

    counter = 0
    while (names[0][0] == "l") and (counter <= len(vertexes)):
        # follow chain of latches with possible negations
        counter += 1
        index = int(re.findall(r"\d+", names[0])[-1])  # latch origin from it's name
        if index % 2 != 0:
            index -= 1
        names = [key for key, value in vertexes.items() if value == index]
        if len(names) < 1:
            return (f"f{number}", index)
        if len(names) > 1:
            raise ValueError(f"Indefinite input {index}")

    if names[0][0] == "l":
        raise ValueError("Infinite latch loop")

    return (names[0], index)


def resolve_input(index: int, vertexes: dict[str, int]) -> list[Union[str, int]]:
    # returns name and edge type for input, skips latches
    if index in [0, 1]:  # const input
        return [str(index), 1]

    positive = True
    if index % 2 != 0:  # edge with negation
        positive ^= True
        index -= 1

    names = [key for key, value in vertexes.items() if value == index]
    if len(names) != 1:
        raise ValueError(f"Indefinite input {index}")

    number = 0
    while (names[0][0] == "l") and (number <= len(vertexes)):
        # follow chain of latches with possible negations
        number += 1
        index = int(re.findall(r"\d+", names[0])[-1])  # latch origin from it's name
        if index % 2 != 0:
            positive ^= True
            index -= 1
        names = [key for key, value in vertexes.items() if value == index]
        if len(names) != 1:
            raise ValueError(f"Indefinite input {index}")

    if names[0][0] == "l":
        raise ValueError("Infinite latch loop")

    return [names[0], int(positive)]


def translate_aig(aig_file: str) -> AigDict:
    input_data = ReadFile(aig_file)
    result: AigDict = {"inputs": [], "outputs": [], "nodes": {}}
    vertexes: dict[str, int] = {}

    # aig header parameters
    variables, inputs, latches, outputs, gates = input_data.get()

    # read file and resolve inputs, outputs and gates' names
    for _ in range(inputs):
        index = input_data.get()[0]
        if (index // 2 > variables) or (f"x{index // 2}" in vertexes):
            # only the unique variable can be an input
            raise ValueError(f"File {aig_file} does not match the format")
        vertexes[f"x{index // 2}"] = index
        result["inputs"].append(f"x{index // 2}")

    for i in range(latches):
        latch = input_data.get()
        if latch[0] <= inputs * 2:
            raise ValueError(f"File {aig_file} does not match the format")
        vertexes[f"l{i}_{latch[1]}"] = latch[0]  # latch's origin in it's name

    output_gate = 1
    for _ in range(outputs):
        output = input_data.get()[0]
        if output % 2 != 0:  # inverted outputs are not supported
            output -= 1

        if output <= 1:  # const output
            result["outputs"].append(str(output))
        elif output <= inputs * 2:  # variable output
            name = f"x{output // 2}"
            if name not in result["inputs"]:
                raise ValueError(f"Indefinite output {name}")
            result["outputs"].append(name)
        else:  # node output
            value = resolve_output(output_gate, output, vertexes)
            vertexes[f"f{output_gate}"] = value[1]
            result["outputs"].append(value[0])
            output_gate += 1

    number_gate = 1
    for _ in range(gates):
        index = input_data.get()[0]
        if index <= inputs * 2:
            raise ValueError(f"File {aig_file} does not match the format")
        name = resolve_gate(number_gate, index, vertexes)
        number_gate += int(name[0] == "y")
        vertexes[name] = index

    # read file again and complete grapth
    input_data = ReadFile(aig_file)
    for _ in range(1 + inputs + latches + outputs):  # skip unnecessary information
        input_data.get()

    for _ in range(gates):
        code = input_data.get()
        gate: list[Union[int, str]] = ["and"]

        gate += resolve_input(code[1], vertexes)
        gate += resolve_input(code[2], vertexes)

        name = list(vertexes.keys())[list(vertexes.values()).index(code[0])]
        result["nodes"][name] = gate

    return result
