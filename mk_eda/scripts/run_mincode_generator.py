import time

from mk_eda.libs.functions.mincode_generator import MincodeGenerator


def main():
    input_str = input('Введите набор (в формате "10011101"), для которого требуется вычислить минкод:\n')
    input_func = [int(elem) for elem in input_str]
    generator = MincodeGenerator()
    start_time = time.time()
    mincode = generator.generate_mincode(input_func)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Полученный минкод: {mincode}. Время вычисления минкода - {execution_time} сек.")


if __name__ == "__main__":
    main()
