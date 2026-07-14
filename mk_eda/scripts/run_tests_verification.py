import argparse

from mk_eda.libs.verification.tests.interface import Interface


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i1", "--input_file1", dest="input_file_name1", required=True)
    parser.add_argument("-i2", "--input_file2", dest="input_file_name2", required=True)
    parser.add_argument("-o", "--output_file", dest="output_file_name2", required=False)
    return parser.parse_args()


def main():
    # Считывание имен файлов
    args = parse_args()

    Interface.run(args.input_file_name1, args.input_file_name2, args.output_file_name2)


if __name__ == "__main__":
    main()
