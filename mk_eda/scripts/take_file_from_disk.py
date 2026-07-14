import requests


def search_file_on_yandex_disk(filename: str) -> None:
    download_url: str = "https://disk.yandex.ru/client/disk/" + filename

    response = requests.get(download_url)

    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
            print("Файл успешно скачан.")
    else:
        print(f"Ошибка при скачивании файла: {response.status_code}")


# TODO: use command-line argument
def main():
    print("Введите имя файла")
    filename = input()
    search_file_on_yandex_disk(filename)


if __name__ == "__main__":
    main()
