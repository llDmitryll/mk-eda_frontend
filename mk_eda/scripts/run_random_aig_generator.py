import argparse
import json
import random
import re
import time
from sys import stdout

from mk_eda.libs.translate.translate_aig import AigDict


def merge(left: AigDict, right: AigDict) -> AigDict:
    inputs_list = list(set(left["inputs"] + right["inputs"]))  # merging inputs

    shift = len(left["nodes"])

    # merdging outputs with renaming
    outputs_list = left["outputs"]
    for output in right["outputs"]:
        if output[0] == "x":
            continue
        number = int(re.findall(r"\d+", output)[-1])
        number += shift
        outputs_list.append(f"y{number}")

    # merging nodes with renaming and fixing inputs
    nodes_dict = left["nodes"]
    for name, info in right["nodes"].items():
        number = int(re.findall(r"\d+", name)[-1])
        number += shift
        name = f"y{number}"
        for node in range(1, 4, 2):
            if str(info[node])[0] != "x":
                number = int(re.findall(r"\d+", str(info[node]))[-1])
                number += shift
                info[node] = f"y{number}"
        nodes_dict[name] = info

    # connecting subtrees on new node
    inputs = (
        f"y{shift}" if shift > 0 else f"x{random.randint(1, len(inputs_list))}",
        f"y{len(nodes_dict)}" if len(nodes_dict) > shift else f"x{random.randint(1, len(inputs_list))}",
    )
    root = (
        f"y{len(nodes_dict) + 1}",
        ["and", inputs[0], random.randint(0, 1), inputs[1], random.randint(0, 1)],
    )
    nodes_dict[root[0]] = root[1]

    return {"inputs": inputs_list, "outputs": outputs_list, "nodes": nodes_dict}


def random_aig(n: int, depth: int, outputs: int) -> AigDict:
    if depth == 0:  # some inputs direct to outputs
        inputs_list = [f"x{k}" for k in range(1, n + 1)]
        if outputs > len(inputs_list):
            outputs = len(inputs_list)
        output_list = random.sample(inputs_list, outputs)
        return {"inputs": inputs_list, "outputs": output_list, "nodes": {}}

    depths = [depth - 1, random.randint(0, depth - 1)]
    random.shuffle(depths)

    left_subtree = random_aig(n, depths[0], 0)
    right_subtree = random_aig(n, depths[1], 0)

    result = merge(left_subtree, right_subtree)

    if outputs > len(result["inputs"]) + len(result["nodes"]):
        outputs = len(result["inputs"]) + len(result["nodes"])

    result["outputs"] = random.sample(result["inputs"] + list(result["nodes"].keys()), outputs)

    return result


def parse_args():
    parser = argparse.ArgumentParser(prog="run_random_aig", description="Generates random AIG with given parameters")

    parser.add_argument("-f", help="output file")
    parser.add_argument("-n", type=int, help="number of variables", default=5)
    parser.add_argument("-o", type=int, help="number of outputs", default=1)
    parser.add_argument("--seed", type=int, help="random seed", default=time.time())

    depth_group = parser.add_argument_group(
        title="depth options", description="depths range for random depth choice or fixed depth"
    )

    depth_group.add_argument("-d", type=int, help="depth of resulting AIG", default=3)
    depth_group.add_argument("--min-depth", dest="min_depth", type=int)
    depth_group.add_argument("--max-depth", dest="max_depth", type=int)

    return parser.parse_args()


# TODO: move arguments parsing to separate function
def main():
    args = parse_args()
    file = stdout
    if args.f is not None:
        file = open(args.f, "w")

    if args.min_depth is not None:
        if args.max_depth is None:
            raise ValueError("none or both of max_depth and min_depth have to be set")

    if args.max_depth is not None:
        if args.min_depth is None:
            raise ValueError("none or both of max_depth and min_depth have to be set")
        if args.min_depth > args.max_depth:
            raise ValueError("min_depth should be less than or equal to max_depth")
        args.d = random.randint(args.min_depth, args.max_depth)

    random.seed(args.seed)
    result = random_aig(args.n, args.d, args.o)
    json.dump(result, file)
    file.write("\n")
    file.close()


if __name__ == "__main__":
    main()
