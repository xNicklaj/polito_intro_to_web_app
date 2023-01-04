import sqlite3
from os.path import dirname, join


def create_connection():
    conn = sqlite3.connect(join(dirname(__file__), "App.db"))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    return (conn, cursor)

def query(sql, param=()):
    conn, cursor = create_connection()
    cursor.execute(sql, param)
    res = cursor.fetchall()
    cursor.close()
    conn.commit()
    conn.close()
    return res