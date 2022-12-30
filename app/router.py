from app import app
from flask import request
from flask_login import login_user
from app.models.podcast import getAllEpisodesInPodcast, getAllPodcasts

import app.models.user as user


@app.route('/')
def home():
    return "Hello, World!"

@app.route('/api/signup', methods=["POST"])
def api_signup():
    res = user.createUserIfAvailable(user.User(
        username=request.form["username"],
        password=request.form["password"],
        is_creator=bool(request.form["is_creator"]),
        display_name=request.form["display_name"]
    ))
    if(res == user.USER_CREATED):
        return "Ok."
    elif (res == user.USERNAME_NOT_AVAILABLE):
        return "Username not available."

@app.route('/api/login', methods=["POST"])
def api_login():
    username = request.form.get("username")
    password = request.form.get("password")

    res = user.verifyCredentials(username, password)
    if res == user.INVALID_USERNAME:
        return "Invalid username."
    elif res == user.PASSWORD_MISMATCH:
        return "Password mismatch."
    
    usr = user.getUserByUsername(username)
    login_user(usr, True)
    return "Logged in."

@app.route("/debug")
def debug():
    print(user.getUserByUsername("tes"))
    print(user.createUserIfAvailable(user.User("test", False, "test", "test")) == user.USER_CREATED)
    print(user.verifyCredentials("test", "test") == user.PASSWORD_ACCEPTED)
    print(user.getUserByUsername("test"))
    p = getAllPodcasts()
    if(len(p) > 0):
        print(p)
        print(getAllEpisodesInPodcast(p[0].podcastid))
    return ""