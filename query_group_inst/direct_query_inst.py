import json
import os
import requests
import re
import urllib.request
from ast import literal_eval as line
from bs4 import BeautifulSoup
from lxml import html
import datetime as dt, datetime
from datetime import datetime
import time
from random import randint

proxies = {"https": "nl2.jooble.com:31280"}

# Обработка json от апарсера (вытягиваю ссылки с json)
sort_arr = []
with open('inst_city.json', 'r', encoding='utf8') as outfile:
    for item in outfile:
        json_data = json.loads(item)
        result = json_data['users']
        for obj in result:
            try:
                result = obj['user']['username']
                url = 'https://www.instagram.com/' + result
                print(url)
                sort_arr.append(url) 
            except KeyError:
                print('e')   

# with open('url_city_ru.json', 'w', encoding='utf8') as res:
#     # json.dump(list(set(sort_arr)), res, indent=2)
#     json.dump(sort_arr, res, indent=2)

with open('list_project.txt','w',encoding='utf-8') as f:
    for pr in sort_arr:
        f.write(str(pr) + '\n')


# Отсеиваем урлы, у которых первый пост старше месяца, количество подисчиков и постов больше 300 и 30 соответственно
# updated_arr = []
# i=0
# def get_data(url):
#     try:
#         r = requests.get(url,
#                         timeout=60,
#                         proxies=proxies)
#         json_string = re.compile(r'window\._sharedData\s=\s(.*);<\/script>', re.MULTILINE).findall(r.text)[0]
#         json_data = json.loads(json_string)
#         # print(json_data)
#         json_data_post = json_data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['count']
#         json_data_follow = json_data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_followed_by']['count']
#         print(json_data_post, json_data_follow)
#         if json_data_post > 30 and json_data_follow > 300:
#             json_data = json_data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges'][0]['node']['taken_at_timestamp']
#             updated = datetime.date((dt.datetime.fromtimestamp(json_data)))
#             currentDate = datetime.date(datetime.today())
#             dif = currentDate - updated
#             d = str(dif)
#             day=re.sub(r'\s+.*', '', d)
#             if day != '0:00:00':
#                 day = int(day)
#                 if day < 30:
#                     updated_arr.append(url)
#             else:
#                 updated_arr.append(url)
#             return updated
#     except IndexError:
#         print(url)
    
# for url in sort_arr:
#     time.sleep(randint(2, 8))
#     get = get_data(url)
#     i+=1
#     print(i)
