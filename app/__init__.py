from flask import Flask, session, request
from flask_session import Session
from flask_login import LoginManager

from os.path import join, dirname

from app.models.user import getUserByUsername
from app.common import History, validateFields


app = Flask(__name__)
app.secret_key = '/FW38^HmsF"zDq|}'
app.config['SESSION_TYPE'] = 'filesystem'
app.config["SESSION_PERMANENT"] = False
app.config["UPLOAD_FOLDER"] = join(dirname(__file__), "tmp")
app.config["MAX_CONTENT_PATH"] = 104857600

# Session configuration
app.config.from_object(__name__)
Session(app)

@app.before_request
def use_history():
    if 'history' not in session:
        session['history'] = History()
    if('/static/' in request.url or '/tickupdate' in request.url or request.url == session['history'].get(0)):
        return
    session['history'].push(request.url)

@app.before_request
def use_media():
    if 'last_played' not in session:
        session['last_played'] = dict()
        session['last_played']['ep'] = None
        session['last_played']['pod'] = None
        session['last_played']['meta'] = {
            'is_playing': False,
            'current_time': 0,
            'tickid': 0
        }
    if '/tickupdate' not in request.url:
        session['last_played']['meta']['tickid'] = 0

@app.before_request
def use_field_validation():
    if not validateFields([request.form[v] for v in request.form]):
        return "ERROR: Data mismatch", 500
    return


@app.before_request
def debug():
    return


# Flask-Login configuration
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(username):
    return getUserByUsername(username)

from app import router