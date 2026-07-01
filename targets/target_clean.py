"""User and config helpers (defect-free reference)."""
import os
import sqlite3
from contextlib import closing


def get_user(db, user_id):
    with closing(sqlite3.connect(db)) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM users WHERE id = ?", (user_id,))
        return cur.fetchone()


def load_config(path):
    try:
        with open(path) as f:
            return f.read()
    except OSError as e:
        raise RuntimeError(f"failed to read config {path}") from e


def get_item(items, index):
    if 0 <= index < len(items):
        return items[index]
    return None


def get_api_key():
    return os.environ["API_KEY"]


def render_name(user):
    if user is None:
        return ""
    return user.name.upper()
