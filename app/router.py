from app import app
from flask import render_template, request, redirect, session
from flask_login import login_user, current_user, login_required, login_manager, logout_user
from os.path import splitext, join 
from werkzeug.exceptions import NotFound


from app.db import query
from app.models.podcast import getAllEpisodesInPodcast, getAllPodcasts
import app.models.user as user
import app.models.episode as episode
import app.models.podcast as podcast
import app.models.comment as comment
from app.common import savefile, timestampToString

login_manager.login_view = "/login"

# Basic endpoints knowledge:
# /* usually accepts a GET request and displays a page
# /api/* usually accepts a POST request and redirect to other pages, or at most displays an error
# /p/* is the user profile endpoint
# /pod/* is the podcast endpoint
# /pod/*/* is the episode endpoint

@app.errorhandler(NotFound)
def notfound_handler():
    return render_template("404.html"), 404

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
    session['last_played']['ep'] = None
    session['last_played']['pod'] = None
    session['last_played']['meta'] = {
        'is_playing': False,
        'current_time': 0,
        'tickid': 0
    }
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
    data["similar"] = []
    data["user"] = dict()
    for p in data["podcast"]:
        data["user"][data["podcast"][p].user_username] = user.getUserByUsername(data["podcast"][p].user_username)
    if(current_user.is_authenticated):
        # Get all categories of all podcasts followed
        categories = [podcast.getPodcastById(p).category for p in user.getUserByUsername(current_user.username).getFollowingPodcasts()]
        # flatten list
        categories = [c for elem in categories for c in elem]
        # Get all episodes of all podcasts with some of those categories
        similar = [pod.getAllEpisodes() for pod in list(filter(lambda p : any(chk in p.category for chk in categories), podcast.getAllPodcasts()))]
        # flatten list
        similar = [e for p in similar for e in p]
        data["similar"] = [(e.podcast_podcastid, e.episodeid) for e in similar]
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

@app.route("/categories")
def categories():
    categories = [i["name"] for i in query("SELECT name FROM category", ())]
    data = list()
    for c in categories:
        episodes = list(filter(lambda e : c in podcast.getPodcastById(e.podcast_podcastid).category, episode.getAllEpisodes()))
        data.append({
            'category': c,
            'episodes': [{
                'episode_meta': e,
                'podcast_meta': podcast.getPodcastById(e.podcast_podcastid)
            } for e in episodes]
        })
    return render_template("categories.html", data=data)

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

@app.route("/new")
@login_required
def new():
    if not current_user.is_creator:
        return redirect("/")
    created = [podcast.rowToObject(q) for q in query("SELECT * FROM podcast WHERE user_username = ?", (current_user.username,))]
    categories = podcast.getAllCategories()
    return render_template("new.html", created=created, categories=categories)

@app.route("/api/new/podcast", methods=["POST"])
@login_required
def newpodcast():
    if not current_user.is_creator:
        return 404.
    if(request.form["newpodcast_description"] == None or request.form["newpodcast_title"] == None):
        return redirect(session["history"].get(-1) + "?err=1004")
    
    categories = list(filter(lambda k : "cat-" in k , request.form.keys()))
    if(len(categories) == 0):
        return "Select a category", 500

    if "image" in request.files["newpodcast_thumbnail"].mimetype:
        f = request.files["newpodcast_thumbnail"]
        filename = str(abs(hash(f.filename))) + splitext(f.filename)[-1]
        savefile(f, join("images", filename))
    else:
        filename = "pod_default.jpg"

        
    p = podcast.createNew(request.form["newpodcast_description"], request.form["newpodcast_title"], filename, current_user.username, categories)
    if(p == podcast.ERR_COULD_NOT_CREATE):
        return redirect(session["history"].get(-1) + "?err=1005")
    return redirect(f"/pod/{p.podcastid}")

@app.route('/pod/', defaults={'podcastid': ''})
@app.route("/pod/<podcastid>", methods=["GET"])
def podcastview(podcastid):
    pod = podcast.getPodcastById(podcastid)
    if(pod == None):
        return notfound_handler()
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

@app.route("/api/new/episode", methods=["POST"])
@login_required
def newepisode():
    if not current_user.is_creator:
        return "Not authorised.", 401.
    if(request.form["newepisode_description"] == None or request.form["newepisode_title"] == None or request.form["newepisode_podcastid"] == None or request.files["newepisode_track"].content_length > 0):
        return redirect("/pod/" +  request.form["newepisode_podcastid"] + "?err=1004")
    if(podcast.getPodcastById(request.form["newepisode_podcastid"]).user_username != current_user.username):
        return redirect("/pod/" +  request.form["newepisode_podcastid"] + "?err=1006")
    
    f = request.files["newepisode_track"]
    if("audio" not in f.mimetype):
        return "ERROR: Data mismatch", 500
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
        return notfound_handler()
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

@app.route('/api/new/comment', methods=["POST"])
@login_required
def newcomment():
    content = request.form["content"]
    username = current_user.username
    podcastid = request.form["podcastid"]
    episodeid = request.form["episodeid"]
    if(content == None or podcastid == None or episodeid == None):
        return redirect(session['history'].get(0) + '?err=1004')
    if(comment.createNew(podcastid, episodeid, username, content) == comment.ERR_COULD_NOT_CREATE):
        return redirect(session['history'].get(0) + '?err=1005')
    return redirect(session['history'].get(0))

@app.route('/play/<podcastid>/<episodeid>', methods=["POST"])
@login_required
def playtrack(podcastid, episodeid):
    if podcastid == None or episodeid == None:
        return redirect(session["history"].get(-1))
    
    pod = podcast.getPodcastById(podcastid)
    try:
        ep = list(filter(lambda e : e.episodeid == int(episodeid), pod.getAllEpisodes()))[0]
    except:
        return redirect(session["history"].get(-1))
    session['last_played']['pod'] = pod
    session['last_played']['ep'] = ep
    session['last_played']['meta']['is_playing'] = True
    session['last_played']['meta']['current_time'] = 0
    session['last_played']['meta']['tickid'] = 0
    return redirect(session["history"].get(-1))

@app.route('/api/tickupdate', methods=["POST"])
def updatetrack():
    is_playing = request.form["isPlaying"] == 'true'
    current_time = request.form["currentTime"]
    tickid = request.form["tickid"]
    playid = request.form["playID"]
    if(is_playing == None or current_time == None):
        return "ERROR: Data mismatch.", 500
    if int(tickid) > session['last_played']['meta']['tickid'] and int(playid.split('_')[0]) == session['last_played']['pod'].podcastid and int(playid.split('_')[1]) == session['last_played']['ep'].episodeid:
        session['last_played']['meta'] = {
            'is_playing': is_playing,
            'current_time': float(current_time),
            'tickid': int(tickid)
        }
    return "Ok.", 200

@app.route('/api/update/episode', methods=["POST"])
@login_required
def updateepisode():
    podcastid = request.form['update_podcastid']
    episodeid = request.form['update_episodeid']
    title = request.form['update_title']
    description = request.form['update_description']
    pod = podcast.getPodcastById(podcastid)
    if(pod == None):
        return "ERROR: Data mismatch.", 500
    if(pod.user_username != current_user.username):
        return 401, "Unauthorized." 
    if int(episodeid) not in [e.episodeid for e in pod.getAllEpisodes()]:
        return "ERROR: Data mismatch.", 500
    query("UPDATE episode SET title = ?, description = ? WHERE podcast_podcastid = ? AND episodeid = ?", (title, description, podcastid, episodeid,))
    return redirect(session["history"].get(0))
            
@app.route('/api/update/podcast', methods=["POST"])
@login_required
def updatepodcast():
    podcastid = request.form['update_podcastid']
    title = request.form['update_title']
    description = request.form['update_description']
    pod = podcast.getPodcastById(podcastid)
    if(pod == None):
        return "ERROR: Data mismatch.", 500
    if(pod.user_username != current_user.username):
        return 401, "Unauthorized." 
    query("UPDATE podcast SET title = ?, description = ? WHERE podcastid = ?", (title, description, podcastid,))
    return redirect(session["history"].get(0))

@app.route('/api/update/comment', methods=["POST"])
@login_required
def updatecomment():
    podcastid = request.form['podcastid']
    episodeid = request.form['episodeid']
    content = request.form['content']
    timestamp = request.form['timestamp']
    if(podcastid == None or episodeid == None or timestamp == None or content == None):
        return "ERROR: Data mismatch.", 500
    res = query("SELECT * FROM comment WHERE episode_podcast_podcastid = ? AND episode_episodeid = ? AND date_published = ? AND user_username = ?", (podcastid, episodeid, timestamp, current_user.username, ))
    if(len(res) == 0): 
        return "ERROR: Data mismatch.", 500
    query("UPDATE comment SET content = ? WHERE episode_podcast_podcastid = ? AND episode_episodeid = ? AND date_published = ? AND user_username = ?", (content, podcastid, episodeid, timestamp, current_user.username, ))
    return redirect(session["history"].get(0))

@app.route('/api/remove/podcast', methods=["POST"])
@login_required
def removepodcast():
    podcastid = request.form['podcastid']
    if(podcastid == None):
        return "ERROR: Data mismatch.", 500
    pod = podcast.getPodcastById(podcastid)
    if(pod.user_username != current_user.username):
        return 401, "Unauthorized." 
    query("DELETE FROM podcast WHERE podcastid = ?", (podcastid,))
    return redirect('/')

@app.route('/api/remove/episode', methods=["POST"])
@login_required
def removeepisode():
    podcastid = request.form['podcastid']
    episodeid = request.form['episodeid']
    pod = podcast.getPodcastById(podcastid)
    if(pod.user_username != current_user.username):
        return 401, "Unauthorized." 
    if int(episodeid) not in [e.episodeid for e in pod.getAllEpisodes()]:
        return "ERROR: Data mismatch.", 500
    query("DELETE FROM episode WHERE podcast_podcastid = ? AND episodeid = ?", (podcastid,episodeid, ))
    return redirect('/pod/'+podcastid)

@app.route('/api/remove/comment', methods=["POST"])
@login_required
def removecomment():
    podcastid = request.form['podcastid']
    episodeid = request.form['episodeid']
    timestamp = request.form['timestamp']
    if(podcastid == None or episodeid == None or timestamp == None):
        return "ERROR: Data mismatch.", 500
    query("DELETE FROM comment WHERE episode_podcast_podcastid = ? AND episode_episodeid = ? AND date_published = ? AND user_username = ?", (podcastid, episodeid, timestamp, current_user.username, ))
    return redirect(session["history"].get(0))

@app.route('/delete/', defaults={'podcastid': ''})
@app.route('/delete/<podcastid>')
@login_required
def deletepodview(podcastid):
    pod = podcast.getPodcastById(podcastid)
    if(pod == None):
        return "ERROR: Data mismatch.", 500
    return render_template("delete.html", pod=pod, ep=None)

@app.route('/delete/', defaults={'podcastid': '', 'episodeid': ''})
@app.route('/delete/<podcastid>/<episodeid>')
@login_required
def deleteepview(podcastid, episodeid):
    pod = podcast.getPodcastById(podcastid)
    if(pod == None):
        return "ERROR: Data mismatch.", 500
    if int(episodeid) not in [e.episodeid for e in pod.getAllEpisodes()]:
        return "ERROR: Data mismatch.", 500
    ep = list(filter(lambda e : e.episodeid == int(episodeid), pod.getAllEpisodes()))[0]
    return render_template("delete.html", pod=pod, ep=ep)

