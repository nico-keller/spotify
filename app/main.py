import os
import pprint
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from flask import Flask, request, redirect, session, url_for
import time

# Load environment variables from a .env file (if it exists)
load_dotenv()

# IMPORTANT: Replace these with your actual Client ID, Client Secret, and Redirect URI.
# It is highly recommended to store these in a .env file for security.
CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT_URI")
print(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)

# Define the scopes (permissions) your app needs.
scope = "user-read-private user-read-email user-library-read user-top-read user-read-recently-played"

# Create a Flask web server instance
app = Flask(__name__)
# A secret key is needed for session management.
# In a real app, this should be a random, long string.
app.secret_key = 'supersecretkey'
app.config['SESSION_COOKIE_NAME'] = 'SpotifySessionCookie'

# The SpotifyOAuth object will handle the authorization process.
sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
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


@app.route("/")
def index():
    """
    Main route. Redirects to Spotify login if not authenticated.
    """
    token_info = get_token()

    if not token_info:
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    # If a token exists, we can now use it.
    return "You are authenticated! Navigate to /profile to see your data."


@app.route("/callback")
def callback():
    """
    Callback route to handle the redirect from Spotify after user authentication.
    """
    # Get the authorization code from the URL parameters
    code = request.args.get('code')

    # Get the access token and ensure it's returned as a dictionary (the default behavior)
    # The original code had as_dict=False, which caused the TypeError.
    token_info = sp_oauth.get_access_token(code)

    # Store the token information in the session
    session['token_info'] = token_info

    return redirect(url_for("profile"))


@app.route("/profile")
def profile():
    """
    Route to display user profile data. Requires a valid token.
    """
    token_info = get_token()
    if not token_info:
        return redirect(url_for("index"))

    try:
        sp = spotipy.Spotify(auth=token_info['access_token'])
        user_profile = sp.me()

        # Get the user's top artists (short term)
        top_artists = sp.current_user_top_artists(limit=5, time_range="short_term")
        top_artists_list = [artist['name'] for artist in top_artists['items']]

        # Get the user's recently played tracks
        recently_played = sp.current_user_recently_played(limit=5)
        recently_played_list = [
            f"{item['track']['name']} by {item['track']['artists'][0]['name']}"
            for item in recently_played['items']
        ]

        # In a real app, you would render an HTML template here with this data.
        # For now, we'll just return a formatted string.
        output = f"""
        <h1>Welcome, {user_profile['display_name']}!</h1>
        <h2>Your Top Artists (last 4 weeks):</h2>
        <ul>
            {''.join([f'<li>{artist}</li>' for artist in top_artists_list])}
        </ul>
        <h2>Your Recently Played Tracks:</h2>
        <ul>
            {''.join([f'<li>{track}</li>' for track in recently_played_list])}
        </ul>
        <a href="{url_for('logout')}">Logout</a>
        """
        return output
    except Exception as e:
        return f"An error occurred: {e}"


@app.route("/logout")
def logout():
    """
    Route to log the user out by clearing the session.
    """
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    # Ensure this port matches your REDIRECT_URI
    app.run(port=8888, debug=True)

