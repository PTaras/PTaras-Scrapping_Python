import configparser
import json
from datetime import date, datetime
from autotitle import auto_tag
import pyodbc
import os
import ftplib
import logging
import requests
import re
import urllib.request
import datetime as dt
import time
from random import randint

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
            """ select url, name from [dbo].[instagram_group] with(nolock) """)
        start_urls = cursor.fetchall()
        lager_connect.commit()

    return start_urls


def dump_all_messages(url):
    """Записывает json-файл с информацией о вакансиях"""
    global result_data, response
    try:
        response = requests.get(url,
                                timeout=60,
                                headers={
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0'},
                                proxies=change_proxy())
    except:
        print('ConnectionResetError')
    time.sleep(randint(10, 30))
    try:
        if response.status_code == 200:
            try:
                json_string = \
                    re.compile(r'window\._sharedData\s=\s(.*);<\/script>', re.MULTILINE).findall(response.text)[0]
                json_data = json.loads(json_string)
                json_data_1 = \
                    json_data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media'][
                        'edges']
                region_serp = json_data['entry_data']['ProfilePage'][0]['graphql']['user']['full_name']
            except KeyError:
                print('Ban ip')

            code_and_text = []
            for item in json_data_1:
                try:
                    desc = item['node']['edge_media_to_caption']['edges'][0]['node']['text']
                except:
                    desc = ''
                link = 'https://www.instagram.com/p/' + item['node']['shortcode']
                date = item['node']['taken_at_timestamp']
                updated = (dt.datetime.fromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S'))
                position = auto_tag(desc)
                try:
                    region = item['node']['location']['name']
                except:
                    region = ''
                code_and_text.append(
                    {"url": link, "position": position, "region": region, "region_1": region_serp, "updated": updated,
                     "desc": desc})
                result_data = {"data": code_and_text}
        else:
            result_data = {'data': []}

        with open(os.path.join('json', '{}.json'.format(url.split('/')[-1])), 'w', encoding='utf8') as outfile:
            json.dump(result_data, outfile, indent=2)
    except IndexError:
        print('IndexError')


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
    logging.info('Start')
    clean_folder()
    main()
    dump_to_ftp()
    logging.info('Finish')
