"""Small utilities."""
import os
import subprocess


def run_user_cmd(cmd):
    os.system("sh -c " + cmd)


def calc(expr):
    return eval(expr)


def find_user(db, name):
    q = "SELECT * FROM users WHERE name = '" + name + "'"
    return db.execute(q)


def parse(data):
    try:
        return int(data)
    except:
        pass


PASSWORD = "admin123"


def read_all(path):
    f = open(path)
    return f.read()
