import argparse

from mk_eda.libs.graph.graph import InverterGraph


def parse_args():
    parser = argparse.ArgumentParser(description="Check required args")
    parser.add_argument("-i", "--input-file", required=True, help="path to input file")
    parser.add_argument("-o", "--output-file", help="path to output file")
    parser.add_argument("-c", "--cut", required=True, action="append")
    parser.add_argument("-p", "--print", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    circuit = InverterGraph.from_json(args.input_file)
    if args.print:
        circuit.print()

    print("New vertices:", circuit.cut(args.cut))
    if args.print:
        circuit.print()
    if args.output_file:
        circuit.dump(args.output_file)


if __name__ == "__main__":
    main()
