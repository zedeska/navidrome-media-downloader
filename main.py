from flask import Flask, request, render_template, redirect, url_for, flash, Blueprint
from flask_login import LoginManager, login_user, login_required
from qobuz_dl.qopy import Client
from qobuz_dl.bundle import Bundle
from qobuz_dl.core import QobuzDL
from encrypt import decrypt, get_enc_key
import sqlite3
from exceptions import UserNotFound
from models import User
from waitress import serve
from config import Config
import multiprocessing

conf = Config()
conf.load()

def get_tokens():
    bundle_ = Bundle()
    app_id = bundle_.get_app_id()
    secrets = [
        secret for secret in bundle_.get_secrets().values() if secret
    ]  # avoid empty fields
    return app_id, secrets

def search(title:str, type:str):
    app_id, secrets = get_tokens()

    client = Client(app_id=app_id, secrets=secrets)
    client.auth(conf.qobuz_email, conf.qobuz_password)

    if type == "album":
        search_result = client.search_albums(title, 20)["albums"]["items"]
    elif type == "track":
        search_result = client.search_tracks(title, 20)["tracks"]["items"]
    return search_result

def get_user_info(username:str = None, user_id:str = None):
    with sqlite3.connect(conf.navidrome_db) as conn:
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

app = Flask(__name__)
bp = Blueprint("main", __name__, template_folder="templates")
app.secret_key = 'super-duper-secret-key'
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id:str):
    try:
        user_info = get_user_info(user_id=user_id)
    except UserNotFound:
        return None
    return User(id=user_info[0], user=user_info[1])


# for dev purposes
"""@app.route("/search", methods=["GET"])
def seah():
    title = request.args.get("title")
    result = search(title, "track")
    return jsonify(result), 200"""


@bp.route("/", methods=["GET", "POST"])
#@login_required
def index():
    if request.method == "POST":
        title = request.form["title"]
        type = request.form["type"]
        return render_template("index.html", results=search(title, type), type=type, base_url=conf.base_url)
    return render_template("index.html", base_url=conf.base_url)

@bp.route("/download", methods=["POST", "GET"])
@login_required
def download():
    id = request.form['id']
    type = request.form['type']
    title = request.form['title']
    #print("OUI")
    try:
        qb = QobuzDL(directory=conf.qobuz_download_path, quality=6, embed_art=True, quality_fallback=False, folder_format="{artist} - {album} ({year})", downloads_db=conf.qobuz_db_path)
        qb.get_tokens()
        qb.initialize_client(conf.qobuz_email, conf.qobuz_password, qb.app_id, qb.secrets)
        multiprocessing.Process(target=qb.download_from_id, args=[id, True if type == "album" else False], daemon=True).start()
        #qb.download_from_id(id, album=True if type == "album" else False)
    except Exception as e:
        flash("{}".format(e))
        print("ERROR")
        return redirect(url_for('main.index'))
    flash(f"{title} : Success")
    return redirect(url_for('main.index'))

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["user"]
        password = request.form["pass"]

        try:
            user_info = get_user_info(username=username)
        except UserNotFound as e:
            flash("{}".format(e))
            return redirect(url_for("main.login"))
        
        encrypted_pass = user_info[1]

        if password == decrypt(get_enc_key(conf.navidrome_PasswordEncryptionKey) ,encrypted_pass):
            user = User(user_info[0], user=username)
            login_user(user, remember=True)
            return redirect(url_for("main.index"))
        else:
            flash("incorrect password")
            return redirect(url_for("main.login"))
    return render_template("login.html", base_url=conf.base_url)

app.register_blueprint(bp, url_prefix=conf.base_url)

if __name__ == "__main__":
    app.run("127.0.0.1", 4444, debug=True)

    #serve(app, host=conf.host, port=conf.port)
