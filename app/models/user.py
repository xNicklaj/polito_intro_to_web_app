from dataclasses import dataclass
from flask_login import UserMixin
from app.db import query
from argon2 import PasswordHasher
from flask_login import login_manager

@dataclass
class User(UserMixin):
    username : str
    password : str
    display_name : str
    is_creator : bool

    def __init__(self, display_name, is_creator, password, username):
        self.display_name = display_name
        self.is_creator = is_creator
        self.password = password
        self.username = username
    
    def get_id(self):
        return self.username

# Methods

def rowToObject(row):
    return User(row["display_name"], row["is_creator"], row["password"], row["username"])

def getUserByUsername(username):
    sql = 'SELECT * FROM user WHERE username = ?'
    try:
        res = query(sql, (username,))[0]
    except:
        return None
    return rowToObject(res)


USERNAME_NOT_AVAILABLE = -1
USER_CREATED = 0
def createUserIfAvailable(user : User):
    if(getUserByUsername(user.username) is not None): 
        return -1
    ph = PasswordHasher()
    sql = "INSERT INTO user VALUES (?, ?, ?, ?)"
    params = (user.username, user.display_name, user.is_creator, ph.hash(user.password),)
    user = query(sql, params)
    return 0

PASSWORD_MISMATCH = -2
INVALID_USERNAME = -1
PASSWORD_ACCEPTED = 0
def verifyCredentials(username, password):
    user = getUserByUsername(username)
    if(user is None): 
        return -1
    ph = PasswordHasher()
    try:
        ph.verify(user.password, password)
        return 0
    except:
        return -2