import json
import pyodbc
import os
import ftplib
import requests
import re
import urllib.request
from ast import literal_eval as le


# Сравнение 2 файлов:
with open('test_1.json', 'r', encoding='utf8') as data1:
    with open('test_2.json', 'r', encoding='utf8') as data2:
        result=list(set(data1) - set(data2))

with open('result.txt', 'w', encoding='utf8') as result1:
    json.dump(result, result1, indent=2, ensure_ascii=False)

