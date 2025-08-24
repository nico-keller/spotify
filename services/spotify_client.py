import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import session, current_app
import time

class SpotifyClient:
    def __init__(self):
        self.client_id = current_app.config['SPOTIFY_CLIENT_ID']
        self.client_secret = current_app.config['SPOTIFY_CLIENT_SECRET']
        self.redirect_uri = current_app.config['SPOTIFY_REDIRECT_URI']

    def _get_auth_manager(self):
        return SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope="user-read-playback-state,user-modify-playback-state,user-read-currently-playing,user-top-read,ugc-image-upload,app-remote-control,streaming,playlist-read-private,playlist-read-collaborative,user-follow-read,user-read-playback-position,user-read-recently-played,user-library-read",
            cache_path=None
        )

    def get_auth_url(self):
        return self._get_auth_manager().get_authorize_url()

    def exchange_code_for_token(self, code):
        token_info = self._get_auth_manager().get_access_token(code)
        session['token_info'] = token_info
        session['token_expires_at'] = int(time.time()) + token_info['expires_in']
        return token_info

    def get_spotify(self):
        token_info = self._ensure_token_valid()
        return spotipy.Spotify(auth=token_info['access_token'])

    def _ensure_token_valid(self):
        token_info = session.get('token_info', None)
        if not token_info:
            raise Exception("No token in session")

        now = int(time.time())
        is_expired = now > session['token_expires_at']

        if is_expired:
            auth_manager = self._get_auth_manager()
            token_info = auth_manager.refresh_access_token(token_info['refresh_token'])
            session['token_info'] = token_info
            session['token_expires_at'] = int(time.time()) + token_info['expires_in']

        return token_info
