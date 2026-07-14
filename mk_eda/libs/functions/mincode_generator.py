import itertools
import logging
from collections.abc import Generator
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MincodeData:
    function: list[int]
    permutation: tuple[int, ...]
    negations: tuple[bool, ...]


class MincodeGenerator:
    def __init__(self):
        self.cache: dict[tuple[int, ...], MincodeData] = {}

    def generate_mincode(self, input_func: list[int]) -> MincodeData:
        input_func_key = tuple(input_func)
        if input_func_key in self.cache:
            return self.cache[input_func_key]
        mincode_data = min(self._all_permutations(input_func), key=lambda x: x.function)
        self.cache[input_func_key] = mincode_data
        logger.info(f"For function {input_func} generated mincode is {mincode_data.function}")
        return mincode_data

    def _process_permutation(
        self, variables: tuple[int, ...], negations: tuple[bool, ...], vars_amount: int, input_func: list[int]
    ) -> MincodeData:
        new_vector: list[int] = []
        for i in range(2**vars_amount):
            value = [(i >> j) & 1 for j in reversed(range(vars_amount))]
            new_value = [value[variables[i]] ^ negations[i] for i in range(vars_amount)]
            new_vector.append(input_func[sum(bit << index for index, bit in enumerate(reversed(new_value)))])
        return MincodeData(new_vector, variables, negations)

    def _count_vars_amount(self, input_func: list[int]) -> int:
        length = len(input_func)
        vars_amount = 0
        while 2**vars_amount < length:
            vars_amount += 1
        if 2**vars_amount != length:
            error_message = f"Invalid truth table length - {input_func}"
            logger.error(error_message)
            raise ValueError(error_message)
        return vars_amount

    def _all_permutations(self, input_func: list[int]) -> Generator[MincodeData, None, None]:
        vars_amount = self._count_vars_amount(input_func)
        for variables in itertools.permutations(range(vars_amount)):
            for negations in itertools.product([False, True], repeat=vars_amount):
                yield self._process_permutation(variables, negations, vars_amount, input_func)
