import os
import pathlib
import sys
from bs4 import BeautifulSoup
import requests
import argparse
from urllib.parse import urlsplit, urljoin
from time import sleep
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Парсер библиотеки www.tululu.org"
    )
    parser.add_argument(
        '--start_id',
        default=1,
        type=int,
        help='Cкачивать с страницы №',
    )
    parser.add_argument(
        '--end_id',
        default=5,
        type=int,
        help='Остановить на странице №',
    )
    args = parser.parse_args()
    return args


def file_extension(url):
    path, filename = os.path.split(urlsplit(url).path)
    return filename


def get_book_info(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    title_tag = soup.find('td', class_='ow_px_td').find('div').find('h1').text.split('::')
    book_name = str(title_tag[0]).replace('\\xa0', ' ').strip()
    book_author = str(title_tag[1]).replace('\\xa0', ' ').strip()
    img_tag = soup.find('div', class_='bookimage').find('img')['src']
    genre_tag = soup.find('span', class_='d_book').find('a')['title']
    comments = [comment.text for comment in soup.select('.texts span')]
    book_id = soup.select_one('.r_comm input[name="bookid"]')['value']
    serialized_book = {
        "id": book_id,
        "title": sanitize_filename(book_name),
        "author": book_author,
        "comments": comments,
        "book_image": img_tag,
        "genre": genre_tag,
        "img_path": os.path.join('img', file_extension(img_tag)),
        "book_path": os.path.join('books', f'{book_name.strip()}.txt')
    }
    return serialized_book


def get_book_by_id(book_id):
    params = {'id': book_id}
    url_book = f"https://tululu.org/txt.php"
    response = requests.get(url_book, params)
    response.raise_for_status()
    book_content = response.content
    check_for_redirect(response=response)
    url = f"https://tululu.org/b{book_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.text, book_content


def download_image(url, book_page_image):
    img_url = urljoin(url, str(book_page_image[1:]))
    folder_name = os.path.join('images', file_extension(img_url))
    pathlib.Path('images').mkdir(parents=True, exist_ok=True)
    response = requests.get(img_url)
    response.raise_for_status()
    with open(folder_name, 'wb') as file:
        file.write(response.content)


def download_txt(book_page_title, book_content):
    book_name = sanitize_filename(book_page_title).strip()
    folder_name = os.path.join('books', f'{book_name}.txt')
    pathlib.Path('books').mkdir(parents=True, exist_ok=True)
    with open(folder_name, 'wb') as file:
        file.write(book_content)


if __name__ == '__main__':
    url = 'https://tululu.org/'
    parsed_arguments = parse_arguments()
    current_book_id = parsed_arguments.start_id
    while current_book_id <= parsed_arguments.end_id:
        try:
            html_book_content, book_content = get_book_by_id(current_book_id)
            book_info = get_book_info(html_book_content)
            download_txt(book_info['title'], book_content)
            print(f"book inf {book_info['img_path']}   {book_info['book_image']}")
            download_image(url, book_info['book_image'])
            current_book_id += 1
        except requests.exceptions.HTTPError:
            print(f'Книга с ID {current_book_id} не существует')
            current_book_id += 1
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
            print("Отсутствие соединения, ожидание 5сек...", file=sys.stderr)
            sleep(5)
