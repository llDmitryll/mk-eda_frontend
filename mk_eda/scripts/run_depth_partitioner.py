import argparse
import os

from mk_eda.libs.common.constants import PROJECT_DIR
from mk_eda.libs.graph.graph import InverterGraph
from mk_eda.libs.verification.partitioner.depth.depth_partitioner import depth_partitioner


def parse_args():
    parser = argparse.ArgumentParser(description="Split circuit from JSON file to parts with given depth")
    parser.add_argument("file", type=str, help="Path to the JSON file")
    parser.add_argument("depth", type=str, help="Max depth of parts")
    return parser.parse_args()


def main():
    args = parse_args()

    file_path = os.path.join(PROJECT_DIR, args.file)

    graph = InverterGraph.from_json(file_path)

    print("Исходный граф:")
    graph.print()

    partition = depth_partitioner(graph, int(args.depth))

    print("Разбиение графа:")
    for sub_graph in partition:
        sub_graph.print()
        print()


if __name__ == "__main__":
    main()
