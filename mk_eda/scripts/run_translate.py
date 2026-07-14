import json
from sys import argv, stdout

from mk_eda.libs.translate.translate_aig import translate_aig


def main():
    if len(argv) < 2:
        print("usage: run_translate file")
        return

    try:
        json.dump(translate_aig(argv[1]), stdout)
        print()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
