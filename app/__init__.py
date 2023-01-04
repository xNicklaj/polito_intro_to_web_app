from flask import Flask
from flask_session import Session
from flask_login import LoginManager

from os.path import join, dirname

from app.models.user import getUserByUsername


app = Flask(__name__)
app.secret_key = '/FW38^HmsF"zDq|}'
app.config['SESSION_TYPE'] = 'filesystem'
app.config["SESSION_PERMANENT"] = False
app.config["UPLOAD_FOLDER"] = join(dirname(__file__), "tmp")
app.config["MAX_CONTENT_PATH"] = 104857600
print(app.config["UPLOAD_FOLDER"])

# Session configuration
app.config.from_object(__name__)
Session(app)

# Flask-Login configuration
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(username):
    return getUserByUsername(username)

from app import router