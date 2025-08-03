import os
import time
from flask import session
from spotipy.oauth2 import SpotifyOAuth

# Define the scopes (permissions) your app needs.
scope = "user-read-private user-read-email user-library-read user-top-read user-read-recently-played"

# The SpotifyOAuth object will handle the authorization process.
sp_oauth = SpotifyOAuth(
    client_id=os.environ.get("SPOTIPY_CLIENT_ID"),
    client_secret=os.environ.get("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.environ.get("SPOTIPY_REDIRECT_URI"),
    scope=scope,
    cache_path=None  # We will handle caching in the session
)


def get_token():
    """
    Helper function to get the Spotify access token from the session.
    Refreshes the token if it has expired.
    """
    token_info = session.get('token_info', None)
    if not token_info:
        return None

    # Check if the token is expired and refresh it if necessary
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if is_expired:
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session['token_info'] = token_info

    return token_info