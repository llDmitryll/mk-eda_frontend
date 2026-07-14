import os
import subprocess


def decompress_file(input_filename: str) -> None:
    if not os.path.isfile(input_filename):
        print("Файл не найден.")
        return

    if not input_filename.endswith(".gz"):
        print("Файл не имеет расширение .gz.")
        return

    try:
        subprocess.run(["gunzip", input_filename], check=True)
        output_filename = input_filename[:-3] + ".txt"
        print(f"Файл расшифрован и сохранен как '{output_filename}'.")
    except subprocess.CalledProcessError:
        print(f"Произошла ошибка при распаковке файла '{input_filename}'.")


def main():
    input_filename = input("Введите имя сжатого файла (с расширением .gz): ")
    decompress_file(input_filename)


if __name__ == "__main__":
    main()
