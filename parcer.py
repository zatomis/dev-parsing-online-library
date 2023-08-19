import os
from environs import Env
from bs4 import BeautifulSoup
import requests

def check_for_redirect(response):
    if response.history:
        if response.history[0].status_code in [301, 302, 303, 304]:
            raise requests.TooManyRedirects

def save_book(url_image, name_image, path_image):
    os.makedirs(path_image, exist_ok=True)
    response = requests.get(url_image)
    response.raise_for_status()
    try:
        check_for_redirect(response=response)
        with open(f"{path_image}{os.sep}{name_image}", 'wb') as file:
            file.write(response.content)
    except requests.TooManyRedirects:
        print('Errors TooManyRedirects')


if __name__ == '__main__':
    env = Env()
    env.read_env()
    # for book_id in range(10):
    #     save_book(f"https://tululu.org/txt.php?id=311{book_id}8", f"book{book_id}.txt", "book")
    url = 'https://tululu.org/b1/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    # print(soup.find('h1'))
    # title_tag = soup.find('body').find('table').find('div').find('h1')
    # title_tag = soup.find('table', class_='tabs').find('tbody').find('tr').find('td')
    # title_tag = soup.find('body').find('table').find('tr')
    title_tag = soup.find('td', class_='ow_px_td').find('div').find('h1').text.split('::')
    print(str(title_tag[0]).replace('\\xa0', ' ').strip())
    print(str(title_tag[1]).replace('\\xa0', ' ').strip())
    # print(title_tag[1])
    # <h1 class="entry-title">Are You Grateful?</h1>
