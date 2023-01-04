from dataclasses import dataclass

from app.db import query
from app.models.comment import getCommentByEpisode, getCommentByUser

from datetime import datetime, timezone
from random import randint


ERR_COULD_NOT_CREATE = -1

@dataclass 
class Episode():
    podcast_podcastid : int
    episodeid : int
    title : str
    release_date : int
    track : str
    description : str
    def __init__(self, podcastid, episodeid, title, release_date, track, description):
        self.podcast_podcastid = podcastid
        self.episodeid = episodeid
        self.title = title
        self.release_date = release_date
        self.track = track
        self.description = description
    
    def getComments(self, username=None):
        commentsonepisode = getCommentByEpisode(self.podcast_podcastid, self.episodeid)
        if(username != None):
            return [c for c in commentsonepisode if c.user_username == username]
        return commentsonepisode

def rowToObject(row):
    return Episode(row["podcast_podcastid"], row["episodeid"], row["title"], datetime.fromtimestamp(row["release_date"]), row["track"], row["description"])

def getEpisodeByPodcastid(podcastid):
    sql = "SELECT * FROM episode WHERE podcast_podcastid = ?"
    params = (podcastid,)
    res = query(sql, params)
    return [rowToObject(p) for p in res]

def createNew(podcast_podcastid=0, title="", description="", track_ext=".wav"):
    release_date = datetime.now(timezone.utc).timestamp()
    episodeid = randint(0, 999999)
    while(query("SELECT * FROM episode WHERE podcast_podcastid = ? AND episodeid = ?", (podcast_podcastid,episodeid,)) != []):
        episodeid = randint(0, 999999)
    track = f"{podcast_podcastid}_{episodeid}{track_ext}"
    sql = "INSERT INTO episode VALUES(?, ?, ?, ?, ?, ?)"
    query(sql, (podcast_podcastid, episodeid, title, release_date, track, description,))
    res = query("SELECT * FROM episode WHERE podcast_podcastid = ? AND episodeid = ?", (podcast_podcastid, episodeid,))
    if(res == []):
        return -1
    return rowToObject(res[0])