import json
import re
import datetime as dt
from datetime import datetime
import pyodbc
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

DATA_BASE_DRIVER = 'driver={SQL Server}'
LAGER_SERVER = config['Lager']['LAGER_SERVER']
LAGER_DATA_BASE = config['Lager']['LAGER_DATA_BASE']
LAGER_USER = config['Lager']['LAGER_USER']
LAGER_PASSWORD = config['Lager']['LAGER_PASSWORD']

with pyodbc.connect(DATA_BASE_DRIVER,
                    host=LAGER_SERVER,
                    user=LAGER_USER,
                    password=LAGER_PASSWORD,
                    database='Scripter',
                    timeout=60) as lager_connect:
    lager_connect.timeout = 60
    cursor = lager_connect.cursor()
    # Обработка json от апарсера по дате и инсерт в базу:
    sort_arr = []
    with open('inst_ua_updated.json', 'r', encoding='utf8') as outfile:
        for line in outfile:
            if line.startswith('{"config"'):
                line = line[:-11]
                json_data = json.loads(line)
                try:
                    json_data_post = json_data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['count']
                    json_data_follow = json_data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_followed_by']['count']
                    if json_data_post > 10 and json_data_follow > 100:
                        json_date = json_data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges'][0]['node']['taken_at_timestamp']
                        updated = datetime.date((dt.datetime.fromtimestamp(json_date)))
                        currentDate = datetime.date(datetime.today())
                        dif = currentDate - updated
                        d = str(dif)
                        day = re.sub(r'\s+.*', '', d)
                        if day != '0:00:00':
                            day = int(day)
                            if day < 30:
                                result = json_data['entry_data']['ProfilePage'][0]['graphql']['user']["username"]
                                # print(result, updated, json_data_follow)
                                url = 'https://www.instagram.com/' + result
                                cursor.execute('INSERT INTO instagram_group (url, name) VALUES (?,?)', (url, result))
                                sort_arr.append(url)
                            # else:
                            #     sort_arr.append('')
                except KeyError:
                    print('KeyError')
                except IndexError:
                    print('IndexError')

with open('upd_arr_ua_to_base.json', 'w', encoding='utf8') as res:
    json.dump(list(set(sort_arr)), res, indent=2)
