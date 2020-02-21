import json
import os

# Обработка json от апарсера (вытягиваю ссылки с json)
sort_arr = []
with open('inst_city_aparser_ua.json', 'r', encoding='utf8') as outfile:
    for item in outfile:
        json_data = json.loads(item)
        result = json_data['users']
        for obj in result:
            try:
                result = obj['user']['username']
                url = 'https://www.instagram.com/' + result
                sort_arr.append(url)
            except KeyError:
                print('e')

            # Сохранить ссылки в json:
with open('url_from_aparser_ua.json', 'w', encoding='utf8') as res:
    # json.dump(list(set(sort_arr)), res, indent=2)
    json.dump(sort_arr, res, indent=2)

# Сохранить ссылки в текстовом формате:
with open('url_from_aparser_ua.txt', 'w', encoding='utf-8') as f:
    for pr in sort_arr:
        f.write((str(pr)) + '\n')
