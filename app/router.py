from app import app
from flask import render_template, request, redirect
from flask_login import login_user, current_user, login_required, login_manager
from app.models.podcast import getAllEpisodesInPodcast, getAllPodcasts

import app.models.user as user

login_manager.login_view = "/login"

@app.route('/signup')
def signup():
    return render_template("signup.html")

@app.route('/api/signup', methods=["POST"])
def api_signup():
    usr = user.User(
        username=request.form["username"],
        password=request.form["password"],
        is_creator=bool(request.form["is_creator"]),
        display_name=request.form["display_name"]
    )
    if(usr.username == '' or usr.password == '' or usr.display_name == ''):
        return redirect("/signup?err=1000")
    res = user.createUserIfAvailable(usr)
    if(res == user.USER_CREATED):
        return redirect("/login", 301)
    elif (res == user.USERNAME_NOT_AVAILABLE):
        return redirect("/signup?err=1001", 301)

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/api/login', methods=["POST"])
def api_login():
    username = request.form.get("username")
    password = request.form.get("password")
    print(username, password)
    res = user.verifyCredentials(username, password)
    if username == '' or res == user.INVALID_USERNAME:
        return redirect("/login?err=1002", 301)
    elif password== '' or res == user.PASSWORD_MISMATCH:
        return redirect("/login?err=1003", 301)
    
    usr = user.getUserByUsername(username)
    login_user(usr, True)
    return redirect("/", 301)

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

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/subscriptions")
def subscriptions():
    return render_template("subscriptions.html")

@app.route("/me")
@login_required
def me():
    return render_template("profile.html")