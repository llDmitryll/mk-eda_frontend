import argparse

from mk_eda.libs.aig.aig import AndInverterGraph
from mk_eda.libs.common.logger import get_logger
from mk_eda.libs.optimization.rewriting import AIGRewriter

logger = get_logger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-file", dest="input_file", required=True)
    parser.add_argument("-o", "--output-ile", dest="output_file")
    return parser.parse_args()


def main():
    args = parse_args()
    aig = AndInverterGraph().from_json(args.input_file)
    opt_aig = AIGRewriter()
    logger.info(f"Before optimization: {len(aig.nodes)} nodes")
    aig = opt_aig.rewrite(aig)
    logger.info(f"After optimization: {len(aig.nodes)} nodes")
    if args.output_file:
        aig.dump(args.output_file)


if __name__ == "__main__":
    main()
