import os
import requests
from environs import Env


def save_book(url_image, name_image, path_image):
    os.makedirs(path_image, exist_ok=True)
    response = requests.get(url_image)
    response.raise_for_status()
    with open(f"{path_image}{os.sep}{name_image}", 'wb') as file:
        file.write(response.content)


if __name__ == '__main__':
    env = Env()
    env.read_env()
    for book_id in range(10):
        save_book(f"https://tululu.org/txt.php?id=311{book_id}8", f"book{book_id}.txt", "book")
