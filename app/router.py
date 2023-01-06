from app import app
from flask import render_template, request, redirect, session
from flask_login import login_user, current_user, login_required, login_manager, logout_user
from os.path import splitext, join 


from app.db import query
from app.models.podcast import getAllEpisodesInPodcast, getAllPodcasts
import app.models.user as user
import app.models.episode as episode
import app.models.podcast as podcast
import app.models.comment as comment
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
        return redirect(session["history"].get(-1) + "?err=1000")
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
    res = user.verifyCredentials(username, password)
    if username == '' or res == user.INVALID_USERNAME:
        return redirect(session["history"].get(-1) + "?err=1002")
    elif password== '' or res == user.PASSWORD_MISMATCH:
        return redirect(session["history"].get(-1) + "?err=1003")
    
    usr = user.getUserByUsername(username)
    login_user(usr, True)
    return redirect("/")

@app.route("/api/signout")
def signout():
    logout_user()
    return redirect("/")

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

    data["categories"] = []
    return render_template("home.html", data=data)


@app.route("/subscriptions")
@login_required
def subscriptions():
    usr = user.getUserByUsername(current_user.username)
    following = [podcast.getPodcastById(f) for f in usr.getFollowingPodcasts()]
    data = list()
    for f in following:
        data.append({
            'podcast_meta': f,
            'episodes_data': f.getAllEpisodes()
        })
    return render_template("subscriptions.html", data=data)

@app.route("/me")
@login_required
def me():
    usr = user.getUserByUsername(current_user.username)
    following = [podcast.getPodcastById(str(p)) for p in usr.getFollowingPodcasts()]
    created = podcast.getPodcastByUsername(usr.username)
    return render_template("profile.html", user=current_user, following=following, getUserByUsername=user.getUserByUsername, created=created)

@app.route('/p/', defaults={'username': ''})
@app.route("/p/<username>", methods=["GET"])
def profile(username):
    usr = user.getUserByUsername(username)
    following = [podcast.getPodcastById(str(p)) for p in usr.getFollowingPodcasts()]
    created = podcast.getPodcastByUsername(usr.username)
    return render_template("profile.html", user=usr, following=following, getUserByUsername=user.getUserByUsername, created=created)

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
        return redirect(session["history"].get(-1) + "?err=1004")
    if request.files["newpodcast_thumbnail"].content_length > 0:
        f = request.files["newpodcast_thumbnail"]
        filename = str(abs(hash(f.filename))) + splitext(f.filename)[-1]
        savefile(f, join("images", filename))
    else:
        filename = "pod_default.jpg"
        
    p = podcast.createNew(request.form["newpodcast_description"], request.form["newpodcast_title"], filename, current_user.username)
    if(p == podcast.ERR_COULD_NOT_CREATE):
        return redirect(session["history"].get(-1) + "?err=1005")
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
    if int(podcastid) in user.getUserByUsername(current_user.username).getFollowingPodcasts():
        query("DELETE FROM following WHERE user_username = ? AND podcast_podcastid = ?", (current_user.username, podcastid,))
    else: 
        query("INSERT INTO following VALUES(?, ?)", (current_user.username, podcastid,))
    return redirect(session["history"].get(-1))

@app.route("/api/newepisode", methods=["POST"])
@login_required
def newepisode():
    if not current_user.is_creator:
        return 404.
    if(request.form["newepisode_description"] == None or request.form["newepisode_title"] == None or request.form["newepisode_podcastid"] == None or request.files["newepisode_track"].content_length > 0):
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


@app.route('/pod/<podcastid>/', defaults={'podcastid': '', 'episodeid': ''})
@app.route("/pod/<podcastid>/<episodeid>", methods=["GET"])
def episodeview(podcastid, episodeid):
    try:
        ep = list(filter(lambda e : int(e.episodeid) == int(episodeid), episode.getEpisodeByPodcastid(podcastid)))[0]
    except:
        return "Not found", 404
    comm = ep.getComments()
    pod = podcast.getPodcastById(ep.podcast_podcastid)
    comments = list()
    for c in comm:
        comments.append({
            'comment_data': c,
            'user_data': user.getUserByUsername(c.user_username)
        })
    is_following = current_user.is_authenticated and len(list(filter(lambda f : f == pod.podcastid, user.getUserByUsername(current_user.username).getFollowingPodcasts()))) > 0
    return render_template("episode.html", ep=ep, comments=comments, pod=pod, is_following=is_following, timestampToString=timestampToString)

@app.route('/api/newcomment', methods=["POST"])
@login_required
def newcomment():
    content = request.form["content"]
    username = current_user.username
    podcastid = request.form["podcastid"]
    episodeid = request.form["episodeid"]
    if(content == None or podcastid == None or episodeid == None):
        return redirect(session['history'].get(-1) + '?err=1004')
    if(comment.createNew(podcastid, episodeid, username, content) == comment.ERR_COULD_NOT_CREATE):
        return redirect(session['history'].get(-1) + '?err=1005')
    return redirect(session['history'].get(-1))

@app.route('/play/<podcastid>/<episodeid>')
@login_required
def playtrack(podcastid, episodeid):
    if podcastid == None or episodeid == None:
        return 'ERROR: Data mismatch.', 404
    
    pod = podcast.getPodcastById(podcastid)
    try:
        ep = list(filter(lambda e : e.episodeid == int(episodeid), pod.getAllEpisodes()))[0]
    except:
        return 'ERROR: Data mismatch.', 404
    session['last_played']['pod'] = pod
    session['last_played']['ep'] = ep
    session['last_played']['meta']['is_playing'] = True
    session['last_played']['meta']['currentTime'] = 0
    session['last_played']['meta']['tickid'] = 0
    return redirect(session["history"].get(-1))

@app.route('/tickupdate', methods=["POST"])
def updatetrack():
    is_playing = request.form["isPlaying"] == 'true'
    current_time = request.form["currentTime"]
    tickid = request.form["tickid"]
    if(is_playing == None or current_time == None):
        return "ERROR: Data mismatch.", 500
    if  int(tickid) > session['last_played']['meta']['tickid']:
        session['last_played']['meta'] = {
            'is_playing': is_playing,
            'current_time': float(current_time),
            'tickid': int(tickid)
        }
    return "Ok.", 200