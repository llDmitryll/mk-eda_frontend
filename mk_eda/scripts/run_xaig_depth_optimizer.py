import argparse

from mk_eda.libs.optimization.xaig_depth_optimizer import XAIGDepthOptimizer
from mk_eda.libs.xaig.xaig import XorAndInverterGraph


# TODO: move arguments parser to separate function, use '-' in parameters
def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("input_file")
    parser.add_argument("-o", "--output_file")
    parser.add_argument("-n", type=int, default=1, help="number of optimization iterations")
    return parser.parse_args()


def main():
    args = parse_args()

    aig = XorAndInverterGraph.from_json(args.input_file)
    opt = XAIGDepthOptimizer()
    aig = opt(aig, args.n)
    if args.output_file:
        aig.dump(args.output_file)
    else:
        aig.print()


if __name__ == "__main__":
    main()
