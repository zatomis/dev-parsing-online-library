from bs4 import BeautifulSoup
import requests
import argparse
from urllib.parse import urlparse
from time import sleep
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError



def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Парсер библиотеки www.tululu.org'
    )
    parser.add_argument(
        '--start_id',
        default=1,
        type=int,
        help='Cкачивать с страницы №',
    )
    parser.add_argument(
        '--end_id',
        default=10,
        type=int,
        help='Остановить на странице №',
    )
    args = parser.parse_args()
    return args

def parse_book_page(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    title_tag = soup.find('td', class_='ow_px_td').find('div').find('h1').text.split('::')
    book_name = str(title_tag[0]).replace('\\xa0', ' ').strip()
    book_author = str(title_tag[1]).replace('\\xa0', ' ').strip()
    img_tag = soup.find('div', class_='bookimage').find('img')['src']
    genre_tag = soup.find('span', class_='d_book').find('a')['title']
    comments = [comment.text for comment in soup.select('.texts span')]

    serialized_book = {
        "title": sanitize_filename(book_name),
        "author": book_author,
        "comments": comments,
        "image_url": img_tag,
        "genre": genre_tag,
    }
    return serialized_book['title']


def create_json_for_book(book_id):
    params = {'id': book_id}
    url_book = f"https://tululu.org/txt.php"
    response = requests.get(url_book, params)
    response.raise_for_status()
    try:
        check_for_redirect(response=response)
        main_url = f"{str(urlparse(url_book).scheme)}://{str(urlparse(url_book).netloc)}"
        url = f"{main_url}/b{book_id}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.TooManyRedirects:
        return ""


if __name__ == '__main__':
    parsed_arguments = parse_arguments()
    current_book_id = parsed_arguments.start_id
    while (current_book_id <= parsed_arguments.end_id):
        try:
            create_json_for_book(current_book_id)
            current_book_id +=1
        except requests.exceptions.HTTPError:
            print(f'Книга с ID {current_book_id} не существует')
            current_book_id += 1
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
            sleep(5)


