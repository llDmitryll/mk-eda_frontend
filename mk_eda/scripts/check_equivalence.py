import argparse

from mk_eda.libs.graph.graph import InverterGraph


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--design-file", required=True, help="path to design circuit")
    parser.add_argument("-g", "--golden-file", required=True, help="path to golden circuit")
    parser.add_argument("-cd", "--check-design", required=True, nargs="+")
    parser.add_argument("-cg", "--check-golden", required=True, nargs="+")
    parser.add_argument("-c", "--cut", action="store_true")
    return parser.parse_args()


def get_cut_vertices(name: str) -> list[str]:
    return input(f"Enter vertices you want to cut {name} circuit:\n").split()


def main():
    args = parse_args()
    design = InverterGraph.from_json(args.design_file)
    golden = InverterGraph.from_json(args.golden_file)

    check_design, check_golden = args.check_design, args.check_golden
    assert len(check_design) == len(check_golden)

    if args.cut:
        check_design = design.cut(check_design)
        check_golden = golden.cut(check_design)

    for design_output, golden_output in zip(check_design, check_golden):
        equal = design[design_output].equivalent(golden[golden_output])  # type: ignore
        print(f"Functions design['{design_output}'] and golden['{golden_output}'] are {'not ' * (1 - equal)}equal.")


if __name__ == "__main__":
    main()
