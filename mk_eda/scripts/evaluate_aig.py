import argparse

from mk_eda.libs.aig.aig import AndInverterGraph


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-file", dest="input_file", required=True)
    parser.add_argument("-p", "--print", dest="print", action="store_true")
    parser.add_argument("-e", "--evaluate", nargs="+", dest="evaluate")
    parser.add_argument("-n", "--node", dest="node")
    return parser.parse_args()


def main():
    args = parse_args()
    aig = AndInverterGraph.from_json(args.input_file)
    if args.print:
        print(aig.nodes)
    if args.evaluate:
        values_dict: dict[str, bool] = dict()
        for i in range(len(args.evaluate) // 2):
            values_dict[args.evaluate[2 * i]] = bool(int(args.evaluate[2 * i + 1]))
        print(aig.evaluate(args.node, values_dict))


if __name__ == "__main__":
    main()
