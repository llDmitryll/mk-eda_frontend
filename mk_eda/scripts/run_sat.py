import argparse
import os
import sys
import time

from mk_eda.libs.common.constants import PROJECT_DIR
from mk_eda.libs.verification.sat.sat import Sat

sys.setrecursionlimit(10000)


def parse_args():
    parser = argparse.ArgumentParser(description="Compare two circuits from JSON files.")
    parser.add_argument("file1", type=str, help="Path to the first JSON file")
    parser.add_argument("file2", type=str, help="Path to the second JSON file")
    parser.add_argument("--check-all", required=False, action="store_true", help="Check all outputs")
    return parser.parse_args()


def main():
    args = parse_args()

    start_time = time.time()

    file1_path = os.path.join(PROJECT_DIR, args.file1)
    file2_path = os.path.join(PROJECT_DIR, args.file2)

    circuit1 = Sat.from_json(file1_path)
    circuit2 = Sat.from_json(file2_path)

    if len(circuit1.outputs) != len(circuit2.outputs):
        print("Схемы реализуют разное количество функций")
        return

    num_equal_functions = 0

    for output in circuit1.outputs:
        unequal_set = Sat.find_unequal_set(circuit1[output], circuit2[output])
        if unequal_set is None:
            num_equal_functions += 1
            print(f"Функции {output} эквивалентны")
        else:
            print(f"Функции {output} не эквивалентны")
            print(f"Набор, где функции отличаются: {unequal_set}")
            if not args.check_all:
                break

    if num_equal_functions == len(circuit1.outputs):
        print(f"Схемы {os.path.relpath(file1_path)} и {os.path.relpath(file2_path)} эквивалентны")
    else:
        print(f"Схемы {os.path.relpath(file1_path)} и {os.path.relpath(file2_path)} не эквивалентны")

    end_time = time.time()
    print(f"Время выполнения: {end_time - start_time} секунд")


if __name__ == "__main__":
    main()
