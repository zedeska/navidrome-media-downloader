import tomllib

class Config():
    def __init__(self):
        self.host = None
        self.port = None
        self.base_url = None
        self.download_path = None

        self.navidrome_db = None
        self.navidrome_PasswordEncryptionKey = None

        self.qobuz_email = None
        self.qobuz_password = None
        self.qobuz_db_path = None

        self.arl = None

    def load(self):
        with open("conf.toml", "rb") as f:
            conf = tomllib.load(f)

        self.host = conf["server"]["host"]
        self.port = conf["server"]["port"]
        self.base_url = conf["server"]["base_url"]
        self.download_path = conf["server"]["download_path"]

        self.navidrome_db = conf["navidrome"]["DbPath"]
        self.navidrome_PasswordEncryptionKey = conf["navidrome"]["PasswordEncryptionKey"]

        self.qobuz_email = conf["qobuz"]["email"]
        self.qobuz_password = conf["qobuz"]["password"]
        self.qobuz_db_path = conf["qobuz"]["DbPath"]

        self.arl = conf["deezer"]["arl"]
