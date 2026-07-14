import gzip
import os
import sys


def compress_file(input_filename: str) -> None:
    if not os.path.isfile(input_filename):
        print("Файл не найден.")
        return

    output_filename = input_filename + ".gz"

    with open(input_filename, "rb") as f_in:
        with gzip.open(output_filename, "wb") as f_out:
            f_out.writelines(f_in)

    print(f"Файл сжат и сохранен как '{output_filename}'.")


def main():
    filename = sys.argv[1]
    compress_file(filename)


if __name__ == "__main__":
    main()
