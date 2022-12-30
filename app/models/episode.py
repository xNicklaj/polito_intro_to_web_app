from dataclasses import dataclass
from datetime import datetime

from app.db import query
from app.models.comment import getCommentByEpisode, getCommentByUser

@dataclass 
class Episode():
    podcast_podcastid : int
    title : str
    release_date : int
    track : str
    def __init__(self, podcastid, title, release_date, track):
        self.podcast_podcastid = podcastid
        self.title = title
        self.release_date = release_date
        self.track = track
    
    def getComments(self, username=None):
        commentsonepisode = getCommentByEpisode(self.podcast_podcastid, self.title)
        if(username != None):
            return [c for c in commentsonepisode if c.user_username == username]
        return commentsonepisode

def rowToObject(row):
    return Episode(row["podcast_podcastid"], row["title"], datetime.fromtimestamp(row["release_date"]), row["track"])

def getEpisodeByPodcastid(podcastid):
    sql = "SELECT * FROM episode WHERE podcast_podcastid = ?"
    params = (podcastid,)
    res = query(sql, params)
    return [rowToObject(p) for p in res]
