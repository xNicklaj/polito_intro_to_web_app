from dataclasses import dataclass

from app.db import query
from app.models.episode import getEpisodeByPodcastid, rowToObject

from random import randint

ERR_COULD_NOT_CREATE = -1

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
    

# Function to transform an sql rot to a python object
def rowToObject(row):
    return Podcast(row["podcastid"], row["description"], row["title"], row["thumbnail"], row["user_username"])

def getAllPodcasts():
    sql = "SELECT * FROM podcast"
    res = query(sql, ())
    return [rowToObject(p) for p in res]

def getPodcastById(podcastid):
    sql = "SELECT * FROM podcast WHERE podcastid = ?"
    params = (podcastid,)
    try:
        return rowToObject(query(sql, params)[0])
    except:
        return None

def getPodcastByUsername(username):
    sql = "SELECT * FROM podcast WHERE user_username = ?"
    params = (username,)
    return [rowToObject(q) for q in query(sql, params)]

def getAllEpisodesInPodcast(podcastid):
    return getEpisodeByPodcastid(podcastid)

def getAllCategories():
    sql = "SELECT name FROM category"
    res = query(sql, ())
    return [r[0] for r in res]

def createNew(description='', title='', thumbnail='', user_username=0, categories=[]):
    sql = "INSERT INTO podcast VALUES(?, ?, ?, ?, ?)"
    podcastid = randint(0, 999999)
    while(query("SELECT * FROM podcast WHERE podcastid = ?", (podcastid,)) != []):
        podcastid = randint(0, 999999)
    query(sql, (podcastid, description, title, thumbnail, user_username,))
    res = query("SELECT * FROM podcast WHERE podcastid = ?", (podcastid,))
    if(res == []):
        return -1
    ret = rowToObject(res[0])
    sql = "INSERT INTO podcast_category VALUES(?, ?)"
    for c in categories:
        cat = c.replace('cat-', '')
        if(query("SELECT * FROM category WHERE name = ?", (cat,)) == []):
            query("INSERT INTO category VALUES(?)", (cat,))
        query(sql, (ret.podcastid, cat,))
    ret = rowToObject(res[0])
    return ret