import random
from itertools import product


# Функция возвращающая список всех наборов длины n
def create_all_tests(n: int) -> list[list[int]]:
    return [list(test) for test in product(range(2), repeat=n)]


# Функция генерирующая новые тесты путем выбора новых из списка оставшихся
def random_selection_of_tests(
    tests_number: int, tests_suite: list[list[int]]
) -> tuple[list[list[int]], list[list[int]]]:
    new_tests: list[list[int]] = []
    remaining_tests = tests_suite.copy()
    tests_number = min(tests_number, len(remaining_tests))
    for _ in range(tests_number):
        rand_test = random.choice(remaining_tests)
        new_tests.append(rand_test)
        remaining_tests.remove(rand_test)
    return new_tests, remaining_tests


# Функция генерирующая новые тесты путем изменения случайной позиции в старом
def generating_tests(
    n: int, tests_number: int, tests_suite: list[list[int]] = []
) -> tuple[list[list[int]], list[list[int]]]:
    new_tests: list[list[int]] = []
    passed_tests = tests_suite.copy()

    if not passed_tests:
        first_test = [random.randint(0, 1) for _ in range(n)]
        passed_tests.append(first_test)
        new_tests.append(first_test)
        tests_number -= 1

    for _ in range(tests_number):
        new_test = []
        while not new_test or new_test in passed_tests:
            old_test = random.choice(passed_tests)
            position = random.randint(0, n - 1)
            new_test = old_test.copy()
            new_test[position] = new_test[position] ^ 1
        new_tests.append(new_test)
        passed_tests.append(new_test)
    return new_tests, passed_tests
