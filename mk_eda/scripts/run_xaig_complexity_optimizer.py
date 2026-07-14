import argparse

from mk_eda.libs.optimization.xaig_complexity_optimizer import XAIGComplexityOptimizer
from mk_eda.libs.xaig.xaig import XorAndInverterGraph


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-file", dest="input_file", type=str, required=True)
    parser.add_argument("-o", "--output_file", dest="output_file", type=str)
    parser.add_argument("-n", "--iterations", type=int, default=1, help="number of optimization iterations")
    return parser.parse_args()


def main():
    args = parse_args()
    opt = XAIGComplexityOptimizer()

    aig = XorAndInverterGraph.from_json(args.input_file)
    aig = opt(aig, args.n)
    aig.dump(args.output_file)


if __name__ == "__main__":
    main()
