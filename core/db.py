import sqlite3
from contextlib import contextmanager


@contextmanager
def get_db(db_path):
    conn = sqlite3.connect(db_path)
    try:
        yield conn
    finally:
        conn.close()


def init_db(db_path):
    with get_db(db_path) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS playback (path TEXT PRIMARY KEY, time REAL, finished INTEGER)''')
        conn.commit()
