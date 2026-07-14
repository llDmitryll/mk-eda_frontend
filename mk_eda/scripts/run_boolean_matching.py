import argparse

from mk_eda.libs.functions.boolean_matching import BooleanMatching


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("verilog1", type=str, help="First verilog file")
    parser.add_argument("verilog2", type=str, help="Second verilog file")
    return parser.parse_args()


def main():
    args = parse_args()
    file1_path = args.verilog1
    file2_path = args.verilog2

    v1 = open(file1_path).read()
    v2 = open(file2_path).read()

    bm = BooleanMatching()
    matches = bm.check_matching(v1, v2)
    if matches is not None:
        for match in matches:
            formatted_match = ", ".join(match[0])
            print(f"possible matches: {formatted_match} for outputs {match[1]} = {match[2]}")
    else:
        print("No match found")


if __name__ == "__main__":
    main()
