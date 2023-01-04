from app import app
from flask import render_template, request, redirect
from flask_login import login_user, current_user, login_required, login_manager, logout_user
from os.path import splitext, join, dirname
from shutil import move as movefile


from app.db import query
from app.models.podcast import getAllEpisodesInPodcast, getAllPodcasts
import app.models.user as user
import app.models.episode as episode
import app.models.podcast as podcast
from app.common import savefile, timestampToString

login_manager.login_view = "/login"

@app.route('/signup')
def signup():
    return render_template("signup.html")

@app.route('/api/signup', methods=["POST"])
def api_signup():
    usr = user.User(
        username=request.form["username"],
        password=request.form["password"],
        is_creator=True if request.form["is_creator"] == 'on' else False,
        display_name=request.form["display_name"]
    )
    if(usr.username == '' or usr.password == '' or usr.display_name == ''):
        return redirect("/signup?err=1000")
    res = user.createUserIfAvailable(usr)
    if(res == user.USER_CREATED):
        return redirect("/login")
    elif (res == user.USERNAME_NOT_AVAILABLE):
        return redirect("/signup?err=1001")

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
        return redirect("/login?err=1002")
    elif password== '' or res == user.PASSWORD_MISMATCH:
        return redirect("/login?err=1003")
    
    usr = user.getUserByUsername(username)
    login_user(usr, True)
    return redirect("/")

@app.route("/api/signout")
def signout():
    logout_user()
    return redirect("/")

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
    data = dict()

    sql = "SELECT * FROM episode ORDER BY release_date DESC"
    all_episodes = [episode.rowToObject(r) for r in query(sql)]
    data["episode"] = dict()
    for e in all_episodes: data["episode"][(e.podcast_podcastid, e.episodeid)] = e
    data["latest"] = [(e.podcast_podcastid, e.episodeid) for e in all_episodes[0:10]]

    sql = "SELECT * FROM podcast"
    all_podcasts = [podcast.rowToObject(r) for r in query(sql)]
    data["podcast"] = dict()
    for p in all_podcasts:
        data["podcast"][p.podcastid] = p
    return render_template("home.html", data=data)


@app.route("/subscriptions")
@login_required
def subscriptions():
    return render_template("subscriptions.html")

@app.route("/me")
@login_required
def me():
    usr = user.getUserByUsername(current_user.username)
    following = [podcast.getPodcastById(str(p)) for p in usr.getFollowingPodcasts()]
    print(following)
    created = podcast.getPodcastByUsername(usr.username)
    return render_template("profile.html", user=current_user, following=following, getUserByUsername=user.getUserByUsername, created=created)

@app.route('/p/', defaults={'username': ''})
@app.route("/p/<username>", methods=["GET"])
def profile(username):
    usr = user.getUserByUsername(username)
    following = [podcast.getPodcastById(str(p)) for p in usr.getFollowingPodcasts()]
    print(following)
    created = podcast.getPodcastByUsername(usr.username)
    return render_template("profile.html", user=current_user, following=following, getUserByUsername=user.getUserByUsername, created=created)

@app.route("/api/upload_demo", methods=["POST"])
@login_required
def upload():
    f = request.files['file']
    f.save(hash(f.filename) + splitext(f.filename)[-1])
    return "Ok"

@app.route("/new")
@login_required
def new():
    if not current_user.is_creator:
        return redirect("/")
    created = [podcast.rowToObject(q) for q in query("SELECT * FROM podcast WHERE user_username = ?", (current_user.username,))]
    return render_template("new.html", created=created)

@app.route("/api/newpodcast", methods=["POST"])
@login_required
def newpodcast():
    if not current_user.is_creator:
        return 404.
    if(request.form["newpodcast_description"] == None or request.form["newpodcast_title"] == None):
        return redirect("/new?err=1004")
    if request.files["newpodcast_thumbnail"] != None:
        f = request.files["newpodcast_thumbnail"]
        filename = str(abs(hash(f.filename))) + splitext(f.filename)[-1]
        savefile(f, join("images", filename))
        
    p = podcast.createNew(request.form["newpodcast_description"], request.form["newpodcast_title"], filename, current_user.username)
    if(p == podcast.ERR_COULD_NOT_CREATE):
        return redirect("/new?err=1005")
    return redirect(f"/pod/{p.podcastid}")

@app.route('/pod/', defaults={'podcastid': ''})
@app.route("/pod/<podcastid>", methods=["GET"])
def podcastview(podcastid):
    pod = podcast.getPodcastById(podcastid)
    if(pod == None):
        return 404
    ep = pod.getAllEpisodes()
    creator = user.getUserByUsername(pod.user_username)
    is_following = current_user.is_authenticated and query("SELECT * FROM following WHERE podcast_podcastid = ? AND user_username = ?", (pod.podcastid, current_user.username,)) != []
    return render_template("podcast.html", pod=pod, ep=ep, creator=creator, is_following=is_following, timestampToString=timestampToString)

@app.route('/api/follow/', defaults={'podcastid': ''})
@app.route('/api/follow/<podcastid>', methods=["POST"])
@login_required
def follow(podcastid):
    print(user.getUserByUsername(current_user.username).getFollowingPodcasts())
    if int(podcastid) in user.getUserByUsername(current_user.username).getFollowingPodcasts():
        query("DELETE FROM following WHERE user_username = ? AND podcast_podcastid = ?", (current_user.username, podcastid,))
    else: 
        query("INSERT INTO following VALUES(?, ?)", (current_user.username, podcastid,))
    return redirect(f"/pod/{podcastid}")

@app.route("/api/newepisode", methods=["POST"])
@login_required
def newepisode():
    if not current_user.is_creator:
        return 404.
    if(request.form["newepisode_description"] == None or request.form["newepisode_title"] == None or request.form["newepisode_podcastid"] == None or request.files["newepisode_track"] == None):
        return redirect("/pod/" +  request.form["newepisode_podcastid"] + "?err=1004")
    if(podcast.getPodcastById(request.form["newepisode_podcastid"]).user_username != current_user.username):
        return redirect("/pod/" +  request.form["newepisode_podcastid"] + "?err=1006")
    
    f = request.files["newepisode_track"]
    ext = splitext(f.filename)[-1]
    e = episode.createNew(request.form["newepisode_podcastid"], request.form["newepisode_title"], request.form["newepisode_description"], ext)
    savefile(f, join("audio", e.track)) 
    if(e == episode.ERR_COULD_NOT_CREATE):
        return redirect("/pod/" +  request.form["newepisode_podcastid"] + "?err=1005")
    return redirect(f"/pod/{e.podcast_podcastid}/{e.episodeid}")