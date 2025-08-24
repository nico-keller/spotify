from functools import wraps
from flask import redirect, url_for, session, g

from services.spotify_client import SpotifyClient


def spotify_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token_info = session.get("token_info")
        if not token_info:
            return redirect(url_for("auth.login"))

        try:
            sp_client = SpotifyClient()
            g.spotify = sp_client.get_spotify()
        except Exception:
            return redirect(url_for("auth.login"))

        return f(*args, **kwargs)
    return decorated_function