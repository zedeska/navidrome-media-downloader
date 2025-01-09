from flask import Flask, request, render_template, redirect, url_for, flash, Blueprint, jsonify
from flask_login import LoginManager, login_user, login_required
from qobuz_dl.qopy import Client
from qobuz_dl.bundle import Bundle
from qobuz_dl.core import QobuzDL
from encrypt import decrypt, get_enc_key
from exceptions import UserNotFound
from models import User
from waitress import serve
from config import Config
from utils import *

conf = Config()
conf.load()

app_id, secrets = get_tokens()
client = Client(app_id=app_id, secrets=secrets)
client.auth(conf.qobuz_email, conf.qobuz_password)

app = Flask(__name__)
bp = Blueprint("main", __name__, template_folder="templates")
app.secret_key = 'super-duper-secret-key'
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id:str):
    try:
        user_info = get_user_info(conf.navidrome_db ,user_id=user_id)
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
@login_required
def index():
    if request.method == "POST":
        title = request.form["title"]
        type = request.form["type"]
        platform = request.form["platform"]
        return render_template("index.html", results=search(title, type, platform, client if platform == "qobuz" else None), type=type, base_url=conf.base_url, platform=platform)
    return render_template("index.html", base_url=conf.base_url)

@bp.route("/download", methods=["POST", "GET"])
@login_required
def download():
    data = request.get_json()
    id = data['id']
    type = data['type']
    title = data['title']
    platform = data['platform']
    
    try:
        if platform == "qobuz":
            download_qobuz(id, type, conf.download_path, conf.qobuz_db_path, client)
        elif platform == "deezer":
            download_deezer(id, conf.download_path, conf.arl)

    except Exception as e:
        return jsonify({"message": "{}".format(e)}), 500
    #flash(f"{title} : Success")
    return jsonify({"message": "success for {}".format(title)}), 200

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["user"]
        password = request.form["pass"]

        try:
            user_info = get_user_info(conf.navidrome_db, username=username)
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
    #app.run("127.0.0.1", 4444, debug=True)

    serve(app, host=conf.host, port=conf.port)
