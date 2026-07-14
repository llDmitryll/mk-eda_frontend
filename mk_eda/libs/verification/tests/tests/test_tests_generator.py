import pytest

from mk_eda.libs.verification.tests.tests_generator import create_all_tests, generating_tests, random_selection_of_tests


@pytest.mark.parametrize(
    "number_of_inputs, number_of_tests, correct_tests",
    [
        (
            2,
            4,
            [
                [0, 0],
                [0, 1],
                [1, 0],
                [1, 1],
            ],
        ),
        (
            3,
            8,
            [
                [0, 0, 0],
                [0, 0, 1],
                [0, 1, 0],
                [0, 1, 1],
                [1, 0, 0],
                [1, 0, 1],
                [1, 1, 0],
                [1, 1, 1],
            ],
        ),
    ],
)
def test_create_all_tests(number_of_inputs: int, number_of_tests: int, correct_tests: list[list[int]]):
    tests = create_all_tests(number_of_inputs)
    assert len(tests) == number_of_tests
    assert tests == correct_tests


@pytest.mark.parametrize(
    "number_of_tests, number_of_generate_tests, tests_suite",
    [
        (
            5,
            5,
            [
                [0, 0, 0],
                [0, 0, 1],
                [0, 1, 0],
                [0, 1, 1],
                [1, 0, 0],
                [1, 0, 1],
                [1, 1, 0],
                [1, 1, 1],
            ],
        ),
        (
            1,
            1,
            [
                [0, 0],
                [0, 1],
                [1, 0],
                [1, 1],
            ],
        ),
        (
            8,
            8,
            [
                [0, 0, 0],
                [0, 0, 1],
                [0, 1, 0],
                [0, 1, 1],
                [1, 0, 0],
                [1, 0, 1],
                [1, 1, 0],
                [1, 1, 1],
            ],
        ),
        (
            14,
            3,
            [
                [0, 1, 0, 1],
                [1, 1, 1, 1],
                [1, 0, 0, 1],
            ],
        ),
    ],
)
def test_random_selection_of_tests(number_of_tests: int, number_of_generate_tests: int, tests_suite: list[list[int]]):
    tests, remaining_tests = random_selection_of_tests(number_of_tests, tests_suite)
    assert len(tests) == number_of_generate_tests
    assert len(remaining_tests) == len(tests_suite) - len(tests)
    for test in tests:
        assert test not in remaining_tests
        assert test in tests_suite
        assert tests.count(test) == 1
    for test in remaining_tests:
        assert test in tests_suite
        assert remaining_tests.count(test) == 1


@pytest.mark.parametrize(
    "number_of_inputs, number_of_tests, number_of_passed_tests, tests_suite",
    [
        (
            10,
            1,
            1,
            [],
        ),
        (
            10,
            30,
            30,
            [],
        ),
        (
            10,
            20,
            22,
            [
                [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
                [1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
            ],
        ),
    ],
)
def test_generating_tests(
    number_of_inputs: int, number_of_tests: int, number_of_passed_tests: int, tests_suite: list[list[int]]
):
    tests, passed_tests = generating_tests(number_of_inputs, number_of_tests, tests_suite)
    assert len(tests) == number_of_tests
    assert len(passed_tests) == number_of_passed_tests
    for test in tests:
        assert test in passed_tests
        assert test not in tests_suite
        assert tests.count(test) == 1
    for test in tests_suite:
        assert test in passed_tests
    for test in passed_tests:
        assert passed_tests.count(test) == 1
