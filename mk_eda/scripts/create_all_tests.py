import argparse

from mk_eda.libs.verification.tests.tests_generator import create_all_tests


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--number", type=int, dest="n", required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    tests = create_all_tests(args.n)
    for test in tests:
        print(test)


if __name__ == "__main__":
    main()
