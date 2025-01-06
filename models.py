from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id:str , user:str = None):
        super().__init__()
        self.id = id
        self.user = user

