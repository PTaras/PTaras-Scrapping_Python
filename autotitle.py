# -*- coding: utf-8
import requests
import json
import re
from sqlalchemy import *
import urllib


# func for deleting non-text
def remove_emojis(data):
    emoj = re.compile("["
                      u"\U0001F600-\U0001F64F"  # emoticons
                      u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                      u"\U0001F680-\U0001F6FF"  # transport & map symbols
                      u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                      u"\U00002500-\U00002BEF"  # chinese char
                      u"\U00002702-\U000027B0"
                      u"\U00002702-\U000027B0"
                      u"\U000024C2-\U0001F251"
                      u"\U0001f926-\U0001f937"
                      u"\U00010000-\U0010ffff"
                      u"\u2640-\u2642"
                      u"\u2600-\u2B55"
                      u"\u200d"
                      u"\u23cf"
                      u"\u23e9"
                      u"\u231a"
                      u"\ufe0f"  # dingbats
                      u"\u3030"
                      "]+", re.UNICODE)
    return re.sub(emoj, '', data)


def read_json(filename):
    if filename:
        with open(filename, 'r', encoding="utf8") as f:
            result = json.load(f)
    return result


def run(stmt):
    rs = stmt.execute()
    return rs


def send_text(text):
    url = 'http://nl10.jooble.com:13306/ua'
    data = '{"id_job":0,"job_text":"%s","job_title":"","compress": false }' % (text)
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url=url, data=data.encode('utf-8'), headers=headers)
    result_of_post = response.json()
    # if result_of_post != {'err': 'Could not decode input data!'}:
    # print(text)
    # print(result_of_post)
    return (result_of_post)


# func for selecting name if you know tag
def select_title(id_key):
    conn_str = 'DRIVER={ODBC Driver 11 for SQL Server};'
    db_file = read_json('ua5.json')
    conn_str += "SERVER=" + db_file["SERVER"] + ";DATABASE=" + db_file["DATABASE"] + ";UID=" + db_file[
        "UID"] + ";PWD=" + db_file["PWD"]
    params = urllib.parse.quote_plus(conn_str)
    db = create_engine('mssql+pyodbc:///?odbc_connect=%s' % params)
    # db.echo = True
    metadata = MetaData(db)
    title = Table('hashtag', metadata, autoload=True)
    s = title.select(title.c.id == id_key)
    result = s.execute()
    result = result.fetchall()
    return result[0][1]


# send json format {{"data":{"desc":desc}}}

def auto_tags(input):
    desc_text = remove_emojis(input)
    desc_text = desc_text.replace('\n', ' ')
    desc_text = desc_text.replace('"', "'")
    result_of_post = send_text(desc_text)
    title = []
    if result_of_post['key']:
        for i in range(len(result_of_post['key'])):
            title.append(select_title(result_of_post['key'][i]))
    else:
        title = None
    return title


def auto_tag(input):
    desc_text = remove_emojis(input)
    desc_text = desc_text.replace('\n', ' ')
    desc_text = desc_text.replace('"', "'")
    result_of_post = send_text(desc_text)
    try:
        if result_of_post['key']:
            title = (select_title(min(result_of_post['key'])))
        else:
            title = None
        return title
    except KeyError:
        print('KeyError autotitle')


def auto_tags_from_file(filename):
    file = read_json(filename)
    for item in file['data']:
        desc_text = remove_emojis(item['desc'])
        desc_text = desc_text.replace('\n', ' ')
        desc_text = desc_text.replace('"', "'")
        item['desc'] = desc_text
        result_of_post = send_text(desc_text)
        item['title'] = []
        if result_of_post['key']:
            item['key'] = result_of_post['key']
            temp_list = []
            for i in range(len(item['key'])):
                temp_list.append(item['key'][i])
            for i in range(len(item['key'])):
                title = select_title(temp_list[i])
                item['title'].append(title)
        else:
            item['key'] = []

    with open('result_data.json', 'w', encoding='utf-8') as f:
        json.dump(file, f, ensure_ascii=False, indent=4)

    return desc_text


def auto_tag_from_file(filename):
    file = read_json(filename)
    for item in file['data']:
        desc_text = remove_emojis(item['desc'])
        desc_text = desc_text.replace('\n', ' ')
        desc_text = desc_text.replace('"', "'")
        item['desc'] = desc_text
        result_of_post = send_text(desc_text)
        item['title'] = []
        if result_of_post['key']:
            item['key'] = result_of_post['key']
            min_key = (min(item['key']))
            title = select_title(min_key)
            item['title'] = title
        else:
            item['key'] = None
            item['title'] = None

    with open('result_data.json', 'w', encoding='utf-8') as f:
        json.dump(file, f, ensure_ascii=False, indent=4)

    return desc_text
