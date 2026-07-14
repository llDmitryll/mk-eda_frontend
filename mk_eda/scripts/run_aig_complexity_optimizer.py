import argparse

from mk_eda.libs.aig.aig import AndInverterGraph
from mk_eda.libs.optimization.aig_complexity_optimizer import AIGComplexityOptimizer


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-file", type=str, required=True)
    parser.add_argument("-o", "--output-file", type=str, required=True)
    parser.add_argument("-n", "--iterations", type=int, default=1, help="number of optimization iterations")
    return parser.parse_args()


def main():
    args = parse_args()
    aig = AndInverterGraph.from_json(args.input_file)
    opt = AIGComplexityOptimizer()
    new_aig = opt(aig, args.iterations)
    new_aig.dump(args.output_file)


if __name__ == "__main__":
    main()
