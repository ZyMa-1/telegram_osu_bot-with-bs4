from bs4 import BeautifulSoup
import requests
import json
from config import shelve_name
import shelve
import config
from shutil import copyfileobj
from zipfile import ZipFile
from random import randint
import os

headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
}


def strip(data):
    l = 0
    r = len(data) - 1
    while data[l] == '\n' or data[l] == ' ':
        l += 1
    while data[r] == '\n' or data[r] == ' ':
        r -= 1
    return data[l:r + 1]


def format_time(sec):
    days = sec // 86400
    sec %= 86400
    hours = sec // 3600
    sec %= 3600
    min = sec // 60
    return f"{days}d {hours}h {min}m"


def get_user_info(username):
    res = requests.get(f"https://osu.ppy.sh/users/{username}", headers=headers)
    soup = BeautifulSoup(res.content, 'html.parser')
    content_res = soup.find(id="json-user")
    if content_res is None:
        return None, None
    user_info = json.loads(strip(content_res.contents[0]))
    content_res = soup.find(id="json-extras")
    user_extras = json.loads(strip(content_res.contents[0]))
    return user_info, user_extras


def get_file(file_id, real_filename):
    res = requests.get(f"https://api.telegram.org/bot{config.TOKEN}/getFile?file_id={file_id}").json()
    file_path = res["result"]["file_path"]
    res = requests.get(f"https://api.telegram.org/file/bot{config.TOKEN}/{file_path}", stream=True)
    with open(real_filename, 'wb') as res_file:
        copyfileobj(res.raw, res_file)
    del res


def get_song(filename):
    with ZipFile(f"temp/{filename}.zip", 'r') as z:
        need_filename = ""
        fl = 0
        filenames = z.namelist()
        for fileName in filenames:
            if fileName.split('.')[-1] == 'mp3':
                if fl:
                    return "err"
                need_filename = fileName
                fl = 1
        z.extract(need_filename, "temp")
        os.rename(f"temp/{need_filename}", f"temp/{filename}.mp3")
        return "ok"


def delete_temp_files(zip_filename=None, mp3_filename=None):
    if not (zip_filename is None):
        os.remove(zip_filename)
    if not (mp3_filename is None):
        os.remove(mp3_filename)


def generate_filename():
    return str(randint(100000, 999999))


# STORAGE METHODS

def set_default_username(chat_id, username):
    chat_id = str(chat_id)
    with shelve.open(shelve_name) as storage:
        storage[chat_id] = username


def get_default_username(chat_id):
    chat_id = str(chat_id)
    with shelve.open(shelve_name) as storage:
        try:
            return storage[chat_id]
        except KeyError:
            return None
