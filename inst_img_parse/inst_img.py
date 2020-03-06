import configparser
import json
from datetime import date, datetime
import pyodbc
import os
import ftplib
import logging
import requests
import re
import urllib.request
import datetime as dt
from random import randint
import json
import re

try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract


# url = 'https://www.instagram.com/rabota_khv'

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


def clean_folder(path='picture'):
    for folder, _, files in list(os.walk(path)):
        for file in files:
            file_dir = os.path.join(folder, file)
            os.remove(file_dir)


clean_folder()


class Aba(object):
    arr = []
    phones = []

    def add_page(self, num):
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        page = pytesseract.image_to_string(Image.open(r'C:\Users\tp\Desktop\newspaper_parser1\picture\local-filename{}.jpg'.format(num)), lang='rus')
        self.phones += re.findall('[0-9]{3}[\s-][0-9]{3}[\s-][0-9]{2}[\s-][0-9]{2}', page)
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
    # print(proxies)
    return proxies


url = 'https://www.instagram.com/rabota_kherson.24na7'

response = requests.get(url,
                        timeout=60,
                        headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'},
                        proxies=change_proxy())

if response.status_code == 200:
    json_string = re.compile(r'window\._sharedData\s=\s(.*);<\/script>', re.MULTILINE).findall(response.text)[0]
    json_data = json.loads(json_string)
    json_data1 = json_data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']
    region_serp = json_data['entry_data']['ProfilePage'][0]['graphql']['user']['full_name']

    i = 0
    code_and_text = []
    result_data = ""
    clean_folder()
    for item in json_data1:
        desc = item['node']['thumbnail_src']
        urllib.request.urlretrieve(desc, "picture/local-filename" + str(i) + ".jpg")
        i += 1
        link = 'https://www.instagram.com/p/' + item['node']['shortcode']
        date = item['node']['taken_at_timestamp']
        updated = (dt.datetime.fromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S'))
        try:
            region = item['node']['location']['name']
        except:
            region = ''
        code_and_text.append({"url": link, "region": region, "region_1": region_serp, "updated": updated, "desc": "", "position": ""})
        result_data = {"data": code_and_text}
    a = Aba()
    for i in range(12):
        # print(i)
        a.add_page(i)
    all_lib = a.arr
    phones_lib = {"data": a.phones}
    for n in range(len(code_and_text)-1):
        # position = auto_tag(desc)
        # print(code_and_text[n])
        code_and_text[n]["desc"] = all_lib[n]
        code_and_text[n]["position"] = get_auto_title(all_lib[n])
        # print(result_data)
else:
    result_data = {"data": []}
with open('rabota_kherson.24na7.json', 'w', encoding='utf8') as outfile:
    json.dump(result_data, outfile, indent=2)
