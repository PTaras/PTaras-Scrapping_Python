import json
import os
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
                    timeout=60) \
                    as lager_connect:
    lager_connect.timeout = 60
    cursor = lager_connect.cursor()

    with open('.json', 'r', encoding='utf8') as outfile:
        for item in ouinst_bytfile:
            json_data = json.loads(item)
            result = json_data['users']
            for obj in result:
                try:
                    result = obj['user']['username']
                    url = 'https://www.instagram.com/' + result
                    cursor.execute('INSERT INTO instagram_group (url, name) VALUES (?,?)', (url, result))
                    # sort_arr.append(tuple(url + result))
                except KeyError:
                    print('e') 
