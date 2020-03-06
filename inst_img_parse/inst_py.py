import configparser
import json
from datetime import datetime
import pyodbc
import os
import ftplib
import logging
import requests
import re
import datetime as dt
import urllib.request
from random import randint

try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

LOG_FOLDER = "logs\\"
logging.basicConfig(filename=LOG_FOLDER + str(datetime.now()).replace(':', '_') + '.txt',
                    level=logging.INFO,
                    format='[%(asctime)s] %(levelname)s\t:  %(message)s',
                    datefmt='%d.%m.%Y-%H:%M:%S')

config = configparser.ConfigParser()
config.read("config.ini")

DATA_BASE_DRIVER = 'driver={SQL Server}'
LAGER_SERVER = config['Lager']['LAGER_SERVER']
LAGER_DATA_BASE = config['Lager']['LAGER_DATA_BASE']
LAGER_USER = config['Lager']['LAGER_USER']
LAGER_PASSWORD = config['Lager']['LAGER_PASSWORD']

FTP_HOST = config['Ftp']['FTP_HOST']
FTP_USER = config['Ftp']['FTP_USER']
FTP_PASSWORD = config['Ftp']['FTP_PASSWORD']


def change_proxy():
    proxies_arr = ["nl2.jooble.com:31280",
                   "nl5.jooble.com:31280",
                   "nl7.jooble.com:31280",
                   "nl11.jooble.com:31280",
                   "nl4.jooble.com:31280",
                   "us1.jooble.com:31280",
                   "us4.jooble.com:31280",
                   "us7.jooble.com:31280",
                   "us8.jooble.com:31280",
                   ]
    proxies = {"http:": proxies_arr[randint(0, len(proxies_arr) - 1)]}
    print(proxies)
    return proxies


def get_start_urls():
    """ Получает с базы данных список urls """
    with pyodbc.connect(DATA_BASE_DRIVER,
                        host=LAGER_SERVER,
                        user=LAGER_USER,
                        password=LAGER_PASSWORD,
                        database=LAGER_DATA_BASE,
                        timeout=60) as lager_connect:
        lager_connect.timeout = 60
        cursor = lager_connect.cursor()
        cursor.execute(
            """ select url, name from [dbo].[instagram_group] with(nolock) where comment like N'img'""")
        start_urls = cursor.fetchall()
        lager_connect.commit()
        print(start_urls)
    return start_urls


def get_auto_title(text: str) -> str:
    auto_title = ''
    url = 'http://nl10.jooble.com:13306/ua'
    payload = {"id_job": 0, "job_text": text, "job_title": "", "compress": False}
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url=url, json=payload, headers=headers)
        keys = response.json().get('key')
    except Exception as e:
        print(e)
        keys = []

    if keys:
        try:
            with pyodbc.connect('DRIVER={ODBC Driver 11 for SQL Server};',
                                host="ua5.jooble.com",
                                user="cqteam",
                                password="retois87nisAL",
                                database="HashtagSurgeon",
                                timeout=60) \
                    as connect:
                connect.timeout = 60
                cursor = connect.cursor()
                cursor.execute('select name from hashtag with(nolock) where id = ?', (min(keys),))
                auto_title = cursor.fetchall()[0][0]
        except Exception as e:
            print(e)
    return auto_title


def dump_all_messages(url):
    """Записывает json-файл с информацией о вакансиях"""
    global result_data, response

    def clean_folder(path='picture'):
        for folder, _, files in list(os.walk(path)):
            for file in files:
                file_dir = os.path.join(folder, file)
                os.remove(file_dir)

    clean_folder()

    class Aba(object):

        arr = []

        def add_page(self, num):
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            page = pytesseract.image_to_string(Image.open(r'C:\Users\tp\Desktop\newspaper_parser1\picture\picture{}.jpg'.format(num)), lang='rus')
            # self.phones += re.findall('[0-9]{3}[\s-][0-9]{3}[\s-][0-9]{2}[\s-][0-9]{2}', page)
            page = page.replace("\n\n", "\n")
            page = re.split("®|©|@", page)
            arr = []
            for element in page:
                to_json = element
                try:
                    if to_json:
                        to_json = to_json.replace('-\n', '')
                        to_json = to_json.replace('\n', ' ')
                        lib = to_json
                        arr.append(lib)
                except:
                    arr = []
            self.arr += arr

    a = Aba()
    for i in range(12):
        # print(i)
        a.add_page(i)

    def change_proxy():
        proxies_arr = ["nl2.jooble.com:31280",
                       "nl5.jooble.com:31280",
                       "nl7.jooble.com:31280",
                       "nl11.jooble.com:31280",
                       "nl4.jooble.com:31280",
                       "us1.jooble.com:31280",
                       "us4.jooble.com:31280",
                       "us7.jooble.com:31280",
                       "us8.jooble.com:31280",
                       ]
        proxies = {"http:": proxies_arr[randint(0, len(proxies_arr) - 1)]}
        print(proxies)
        return proxies

    # url = 'https://www.instagram.com/rabota_khv'

    response = requests.get(url,
                            timeout=60,
                            headers={
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'},
                            proxies=change_proxy())
    try:
        if response.status_code == 200:
            json_string = re.compile(r'window\._sharedData\s=\s(.*);<\/script>', re.MULTILINE).findall(response.text)[0]
            json_data = json.loads(json_string)
            json_data1 = json_data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']
            region_serp = json_data['entry_data']['ProfilePage'][0]['graphql']['user']['full_name']

            i = 0
            code_and_text = []
            for item in json_data1:
                i += 1
                desc = item['node']['thumbnail_src']
                urllib.request.urlretrieve(desc, "picture/picture" + str(i) + ".jpg")
                link = 'https://www.instagram.com/p/' + item['node']['shortcode']
                date = item['node']['taken_at_timestamp']
                updated = (dt.datetime.fromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S'))
                try:
                    region = item['node']['location']['name']
                except:
                    region = ''
                # position = auto_tag(desc)
                code_and_text.append({"url": link, "region": region, "region_1": region_serp, "updated": updated, "desc": "", "position": ""})
                result_data = {"data": code_and_text}
                for n in range(len(code_and_text)):
                    # position = auto_tag(desc)
                    # print(code_and_text[n])
                    code_and_text[n]["desc"] = a.arr[n]
                    code_and_text[n]["position"] = get_auto_title(a.arr[n])
        else:
            result_data = {"data": []}
        with open(os.path.join('json', '{}.json'.format(url.split('/')[-1])), 'w', encoding='utf8') as outfile:
            json.dump(result_data, outfile, indent=2)
    except IndexError:
        print('error')


def dump_to_ftp():
    """ Отправляет на ftp файлы-результаты парсинга """
    ftp_connection = ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASSWORD)
    for folder, _, files in os.walk('json'):
        for file in files:
            file_dir = os.path.join(folder, file)
            with open(file_dir, 'rb') as file:
                send = ftp_connection.storbinary(
                    "STOR " + os.path.basename(file_dir), file)


def clean_folder(path='json'):
    """" Чистит папку где сохранены json`ы с прошлого парсинга """
    for folder, _, files in list(os.walk(path)):
        for file in files:
            file_dir = os.path.join(folder, file)
            os.remove(file_dir)


def main():
    start_urls = get_start_urls()
    # start_urls = [('https://www.instagram.com/rabota_kiev_ua', '')]
    for url, _ in start_urls:
        logging.info(f'Processing: {url}')
        try:
            dump_all_messages(url)
        except Exception as e:
            print(e)
            logging.exception(f'{url} {inst_group_name} with error')


if __name__ == '__main__':
    # logging.info('Start')
    # clean_folder()
    # date_start = datetime.now()
    # print(date_start)
    main()
    dump_to_ftp()
    # date_end = datetime.now()
    # print(date_end)
    logging.info('Finish')
