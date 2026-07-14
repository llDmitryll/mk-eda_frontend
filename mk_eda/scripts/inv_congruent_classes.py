import itertools
from collections import defaultdict


def apply_permutation_inversion(n: int, func: int, permutation: tuple[int, ...], inversion: tuple[int, ...]) -> int:
    func_bits = [(func >> i) & 1 for i in range(2**n)]
    new_func_bits = [0] * (2**n)

    for i in range(2**n):
        input_bits = [(i >> j) & 1 for j in range(n)]
        permuted_bits = [input_bits[permutation[j]] ^ inversion[j] for j in range(n)]

        new_index = sum([permuted_bits[j] << j for j in range(n)])
        new_func_bits[new_index] = func_bits[i]

    new_func = sum([new_func_bits[i] << i for i in range(2**n)])
    return new_func


def build_equivalence_classes(n: int) -> defaultdict[int, set[int]]:
    classes: defaultdict[int, set[int]] = defaultdict(set)

    for func in range(2 ** (2**n)):
        found = False
        for rep in classes:
            if func in classes[rep]:
                found = True
                break
        if found:
            continue

        new_class: set[int] = set()
        new_class.add(func)

        permutations = list(itertools.permutations(range(n)))
        inversions = list(itertools.product([0, 1], repeat=n))
        for perm in permutations:
            for inv in inversions:
                equivalent_func: int = apply_permutation_inversion(n, func, perm, inv)
                new_class.add(equivalent_func)

        min_representative = min(new_class)
        classes[min_representative] = new_class

    return classes


def save_classes_to_file(n: int, classes: defaultdict[int, set[int]]):
    filename = f"functions_classes{n}.txt"
    with open(filename, "w") as file:
        for _, (rep, _) in enumerate(classes.items()):
            file.write(f"{bin(rep)[2:].zfill(2 ** n)}\n")
    print(f"All classes saved to '{filename}'")


def main():
    n = 2
    classes: defaultdict[int, set[int]] = build_equivalence_classes(n)
    save_classes_to_file(n, classes)
    print(f"Total classes found: {len(classes)}")


if __name__ == "__main__":
    main()
