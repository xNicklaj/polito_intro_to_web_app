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

# Defines a middleware that hooks in before the request is server to the router and pushes the request URL into the client history
# unless it's calling an API or asking for a static resource.
@app.before_request
def use_history():
    if 'history' not in session:
        session['history'] = History()
    if('/static/' in request.url or request.url == session['history'].get(0) or 'api' in request.url):
        return
    session['history'].push(request.url)

# Defines a middleware that hooks in before each request to define the last_played object if it's not defined.
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
    # resets the tickid whenever the user changes page
    if '/api/tickupdate' not in request.url:
        session['last_played']['meta']['tickid'] = 0

# Defines a middleware that automatically validates entries in POST requests
@app.before_request
def use_field_validation():
    if not validateFields([request.form[v] for v in request.form]):
        return "ERROR: Data mismatch", 500
    return


# Flask-Login configuration
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(username):
    return getUserByUsername(username)

# Initialize router
from app import router