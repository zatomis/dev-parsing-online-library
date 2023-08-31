import os
from environs import Env
from bs4 import BeautifulSoup
import requests
import argparse
from urllib.parse import urlparse
from urllib.parse import urljoin
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        if response.history[0].status_code in [301, 302, 303, 304]:
            raise requests.TooManyRedirects


def clear_comment(comment):
    return str(comment).replace('<span class="black">книге:</span>','').replace('<span class="black">','').replace('</span>','').replace('- перейти к книгам этого жанра','').strip()


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
    comments = []
    comment_tag = soup.find_all('span', class_='black')
    for comment in comment_tag:
        if(clear_comment(comment)):
            comments.append({
                'text': clear_comment(comment),
            })

    serialized_book = {
        "title": sanitize_filename(book_name),
        "author": book_author,
        "comments": comments,
        "image_url": img_tag,
        "genre": clear_comment(genre_tag),
    }
    return serialized_book


def download_txt(url_book, path_image='book'):
    os.makedirs(path_image, exist_ok=True)
    response = requests.get(url_book)
    response.raise_for_status()
    try:
        check_for_redirect(response=response)
        book_id = url_book.split('=')[-1]
        book_text = response.content
        main_url = f"{str(urlparse(url_book).scheme)}://{str(urlparse(url_book).netloc)}"
        url = f"{main_url}/b{book_id}"
        response = requests.get(url)
        response.raise_for_status()
        print(parse_book_page(response.text))
        print("")

        return os.path.join(path_image, name_image)
    except requests.TooManyRedirects:
        return ""


if __name__ == '__main__':
    env = Env()
    env.read_env()
    parsed_arguments = parse_arguments()
    for book_id in range(parsed_arguments.start_id, parsed_arguments.end_id):
        download_txt(f"https://tululu.org/txt.php?id={book_id}")


