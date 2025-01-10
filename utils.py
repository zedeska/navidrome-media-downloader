from qobuz_dl.bundle import Bundle
from qobuz_dl.core import QobuzDL
from exceptions import UserNotFound
import requests
import sqlite3
from deezer.api import API
import multiprocessing
from deemix.__main__ import download as dm_download

def get_tokens():
    bundle_ = Bundle()
    app_id = bundle_.get_app_id()
    secrets = [
        secret for secret in bundle_.get_secrets().values() if secret
    ]  # avoid empty fields
    return app_id, secrets

def search_qobuz(title:str, type:str, client):
    if type == "album":
        search_result = client.search_albums(title, 20)["albums"]["items"]
    elif type == "track":
        search_result = client.search_tracks(title, 20)["tracks"]["items"]
    return search_result

def search_deezer(title:str, type:str):
    api = API(headers={}, session=requests.Session())
    return api.search_album(title)["data"] if type == "album" else api.search_track(title)["data"]

def search(title:str, type:str, platform:str, client = None):
    return search_qobuz(title, type, client) if platform == "qobuz" else search_deezer(title, type)

def get_user_info(db_path:str, username:str = None, user_id:str = None):
    with sqlite3.connect(db_path) as conn:
        if user_id:
            res = conn.execute("SELECT id, user_name FROM user WHERE id=?", (user_id,)).fetchone()
            if res == None:
                raise UserNotFound("User not found")
            else:
                return res

        res = conn.execute("SELECT id, password FROM user WHERE user_name=?", (username,)).fetchone()
        if res == None:
            raise UserNotFound("User not found")
        else:
            return res
        
def download_qobuz(id, type, dir, db_path, client):
    qb = QobuzDL(directory=dir, quality=6, embed_art=True, quality_fallback=False, folder_format="{artist} - {album} ({year})", downloads_db=db_path)
    qb.client = client
    qb.download_from_id(id, True if type == "album" else False)
    return

def download_deezer(id, dir, arl):
    dm_download([id], 9, dir, arl)
    return
