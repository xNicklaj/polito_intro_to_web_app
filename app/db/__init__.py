import sqlite3
from os.path import dirname, join

# Create a connection to the database in app/db/App.db, then return both connection and cursor
def create_connection():
    conn = sqlite3.connect(join(dirname(__file__), "App.db"))
    conn.execute("PRAGMA foreign_keys = 1")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    return (conn, cursor)

# Perform a query in the database with automatic handling of the database connection. Returns the result of the query.
def query(sql, param=()):
    conn, cursor = create_connection()
    cursor.execute(sql, param)
    res = cursor.fetchall()
    cursor.close()
    conn.commit()
    conn.close()
    return res