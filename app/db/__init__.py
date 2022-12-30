from app import __root__
from os.path import join, dirname
import sqlite3


def create_connection():
    conn = sqlite3.connect(join(__root__, "db", "App.db"))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    return (conn, cursor)

def query(sql, param):
    conn, cursor = create_connection()
    cursor.execute(sql, param)
    res = cursor.fetchall()
    cursor.close()
    conn.commit()
    conn.close()
    return res