"""User and config helpers."""
import sqlite3
import os


def get_user(db, user_id):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM users WHERE id = " + str(user_id))
    row = cur.fetchone()
    return row


def load_config(path):
    try:
        f = open(path)
        return f.read()
    except Exception:
        return None


def get_item(items, index):
    if index <= len(items):
        return items[index]
    return None


API_KEY = "sk-live-9f8c2b1a7d6e5f4c3b2a1908"


def render_name(user):
    return user.name.upper()
