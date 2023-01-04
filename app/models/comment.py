from dataclasses import dataclass
from app.db import query
from datetime import datetime, timezone

ERR_COULD_NOT_CREATE = -1
@dataclass
class Comment():
    episode_podcast_podcastid : int
    episode_episodeid : str
    user_username : str
    date_published : int
    content : str

    def __init__(self, episode_podcast_podcastid, episode_episodeid, user_username, date_published, content):
        self.episode_podcast_podcastid = episode_podcast_podcastid
        self.episode_episodeid = episode_episodeid
        self.user_username = user_username
        self.date_published = date_published
        self.content = content
    
def rowToObject(row):
    return Comment(row["episode_podcast_podcastid"], row["episode_episodeid"], row["user_username"], row["date_published"], row["content"])

def getCommentByEpisode(podcastid, episodeid):
    sql = "SELECT * FROM comment WHERE episode_podcast_podcastid = ? AND episode_episodeid = ? ORDER BY date_published DESC"
    params = (podcastid, episodeid,)
    res = query(sql, params)
    return [rowToObject(c) for c in res]

def getCommentByUser(username):
    sql = "SELECT * FROM episode WHERE user_username = ?"
    params = (username,)
    res = query(sql, params)
    return [rowToObject(c) for c in res]

def createNew(episode_podcast_podcastid, episode_episodeid, user_username, content):
    sql = "INSERT INTO comment VALUES(?, ?, ?, ?, ?)"
    date_published = datetime.now(timezone.utc).timestamp()
    if(query("SELECT * FROM comment WHERE episode_podcast_podcastid = ? AND episode_episodeid = ? AND user_username = ? AND date_published = ?", (episode_podcast_podcastid, episode_episodeid, user_username, date_published, )) != []):
        return -1
    params = (episode_podcast_podcastid, episode_episodeid, user_username, date_published, content,)
    query(sql, params)
    res = query("SELECT * FROM comment WHERE episode_podcast_podcastid = ? AND episode_episodeid = ? AND user_username = ? AND date_published = ?", (episode_podcast_podcastid, episode_episodeid, user_username, date_published,))
    if(res == []):
        return -1
    return rowToObject(res[0])
