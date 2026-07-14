import pytest

from mk_eda.libs.functions.mincode_generator import MincodeData, MincodeGenerator


def to_binary(number: int, vars_amount: int) -> list[int]:
    return [(number >> 2**vars_amount - i - 1) & 1 for i in range(2**vars_amount)]


@pytest.mark.parametrize(
    "input_value, expected_value, vars_amount",
    [
        (1, MincodeData(to_binary(1, 1), (0,), (False,)), 1),
        (2, MincodeData(to_binary(1, 1), (0,), (True,)), 1),
        (9, MincodeData(to_binary(6, 2), (0, 1), (False, True)), 2),
        (12, MincodeData(to_binary(3, 2), (0, 1), (True, False)), 2),
        (183, MincodeData(to_binary(111, 3), (1, 0, 2), (False, False, True)), 3),
        (199, MincodeData(to_binary(61, 3), (0, 1, 2), (False, True, False)), 3),
        (23216, MincodeData(to_binary(892, 4), (1, 0, 3, 2), (True, True, False, True)), 4),
        (56489, MincodeData(to_binary(5870, 4), (2, 1, 0, 3), (False, True, True, False)), 4),
        (2590353468, MincodeData(to_binary(27180689, 5), (2, 1, 3, 4, 0), (True, False, True, False, True)), 5),
        (3706903305, MincodeData(to_binary(108984435, 5), (0, 1, 2, 3, 4), (True, True, False, True, False)), 5),
    ],
)
def test_mincode_generator(input_value: int, expected_value: MincodeData, vars_amount: int):
    binary_inp = to_binary(input_value, vars_amount)
    generator = MincodeGenerator()
    data = generator.generate_mincode(binary_inp)
    assert data == expected_value
    assert list(generator.cache.values())[0] == expected_value
