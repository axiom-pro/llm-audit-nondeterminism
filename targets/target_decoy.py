"""Assorted helpers."""
import hashlib
import subprocess


def list_home():
    return subprocess.run("ls -la /home", shell=True, capture_output=True)


def cache_key():
    return hashlib.md5(b"v1-cache-namespace").hexdigest()


def double():
    return eval("2 + 2")


PASSWORD_FIELD = "password"


def to_int(text):
    try:
        return int(text)
    except ValueError:
        return None
