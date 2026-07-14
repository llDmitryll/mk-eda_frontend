import argparse

from mk_eda.libs.converter.converter_to_aig import convert_binary_vectors_to_aig


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, required=True)
    parser.add_argument("-o", "--output", type=str, required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    convert_binary_vectors_to_aig(args.input, args.output)


if __name__ == "__main__":
    main()
