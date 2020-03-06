import json
import re

try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract


class Aba(object):
    arr = []
    phones = []

    def add_page(self, num):
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        page = pytesseract.image_to_string(Image.open(r'C:\Users\tp\Desktop\newspaper_parser1\v_karmane\page{}.jpg'.format(num)), lang='rus')
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
                    lib = {"id": hash(to_json), "title": to_json, "desc": to_json}
                    arr.append(lib)
            except:
                arr = []
        self.arr += arr


# all_file = '{"data":['
a = Aba()
for i in range(32):
    print(i)
    a.add_page(i)
all_lib = {"data": a.arr}
phones_lib = {"data": a.phones}

with open('data.json', 'w', encoding="utf-8") as json_file:
    json.dump(all_lib, json_file, ensure_ascii=False)

with open('phones.json', 'w', encoding="utf-8") as json_file:
    json.dump(phones_lib, json_file, ensure_ascii=False)

# print(all_lib)
