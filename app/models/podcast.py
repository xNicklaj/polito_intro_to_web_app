from dataclasses import dataclass

from app.db import query
from app.models.episode import getEpisodeByPodcastid, rowToObject

@dataclass 
class Podcast():
    podcastid : int
    description : str
    title : str
    thumbnail : str
    user_username : str
    category : list
    def __init__(self, podcastid, description, title, thumbnail, user_username):
        self.podcastid = podcastid
        self.description = description
        self.title = title
        self.thumbnail = thumbnail
        self.user_username = user_username

        sql = "SELECT category_name FROM podcast_category WHERE podcast_podcastid = ?" 
        res = query(sql, (self.podcastid,))
        self.category = [r[0] for r in res]

    def getAllEpisodes(self):
        return getEpisodeByPodcastid(self.podcastid)

def rowToObject(row):
    return Podcast(row["podcastid"], row["description"], row["title"], row["thumbnail"], row["user_username"])

def getAllPodcasts():
    sql = "SELECT * FROM podcast"
    res = query(sql, ())
    return [rowToObject(p) for p in res]

def getPodcastById(podcastid):
    sql = "SELECT * FROM podcast WHERE podcastid = ?"
    params = (podcastid)
    return rowToObject(query(sql, params)[0])

def getAllEpisodesInPodcast(podcastid):
    return getEpisodeByPodcastid(podcastid)

def getAllCategories():
    sql = "SELECT name FROM category"
    res = query(sql, ())
    return [r[0] for r in res]

