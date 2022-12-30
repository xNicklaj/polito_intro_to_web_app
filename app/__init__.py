from flask import Flask, session, request
from flask_session import Session
from flask_login import LoginManager
from os.path import dirname, join

app = Flask(__name__)
app.secret_key = '/FW38^HmsF"zDq|}'
app.config['SESSION_TYPE'] = 'filesystem'
app.config["SESSION_PERMANENT"] = False

__root__ = join(dirname(dirname(__file__)), "app")

# Session configuration
app.config.from_object(__name__)
Session(app)

# Flask-Login configuration
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

from app import router