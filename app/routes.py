from flask import Blueprint, request, redirect, session, url_for, render_template, jsonify
import spotipy
from .auth import sp_oauth, get_token

# A Blueprint allows us to organize related routes in a modular way.
bp = Blueprint('routes', __name__)


def _get_spotify_client():
    """Helper function to get a Spotipy client object."""
    token_info = get_token()
    if not token_info:
        return None
    return spotipy.Spotify(auth=token_info['access_token'])


def _get_user_info(sp):
    """Fetches user profile data."""
    return sp.me()


def _get_playlists(sp):
    """Fetches user's playlists."""
    return sp.current_user_playlists(limit=10)


def _get_top_artists(sp):
    """Fetches user's top artists."""
    return sp.current_user_top_artists(limit=5, time_range="short_term")


def _get_top_tracks(sp):
    """Fetches user's top tracks."""
    return sp.current_user_top_tracks(limit=5, time_range="short_term")


def _get_recently_played(sp):
    """Fetches user's recently played tracks."""
    return sp.current_user_recently_played(limit=5)


@bp.route("/")
def index():
    """
    Main route. Redirects to Spotify login if not authenticated, otherwise to the overview page.
    """
    token_info = get_token()

    if not token_info:
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    return redirect(url_for("routes.overview"))


@bp.route("/callback")
def callback():
    """
    Callback route to handle the redirect from Spotify after user authentication.
    """
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info

    return redirect(url_for("routes.overview"))


@bp.route("/overview")
def overview():
    """
    Route to display the main Spotify dashboard.
    Fetches multiple data points and renders the overview.html template.
    """
    sp = _get_spotify_client()
    if not sp:
        return redirect(url_for("routes.index"))

    try:
        user_profile = _get_user_info(sp)
        playlists = _get_playlists(sp)
        top_artists = _get_top_artists(sp)
        top_tracks = _get_top_tracks(sp)
        recently_played = _get_recently_played(sp)

        return render_template(
            "overview.html",
            user_profile=user_profile,
            playlists=playlists['items'],
            top_artists=top_artists['items'],
            top_tracks=top_tracks['items'],
            recently_played=recently_played['items']
        )
    except Exception as e:
        return f"An error occurred: {e}"


@bp.route("/search")
def search():
    """
    API endpoint to search for tracks or artists.
    """
    sp = _get_spotify_client()
    if not sp:
        return jsonify({"error": "Authentication failed."}), 401

    query = request.args.get('q', '')
    search_type = request.args.get('type', 'track')

    if not query:
        return jsonify({"error": "Query parameter 'q' is required."}), 400

    try:
        results = sp.search(q=query, type=search_type, limit=10)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/play", methods=["POST"])
def play():
    """
    API endpoint to play a track.
    """
    sp = _get_spotify_client()
    if not sp:
        return jsonify({"error": "Authentication failed."}), 401

    try:
        sp.start_playback()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/pause", methods=["POST"])
def pause():
    """
    API endpoint to pause playback.
    """
    sp = _get_spotify_client()
    if not sp:
        return jsonify({"error": "Authentication failed."}), 401

    try:
        sp.pause_playback()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/next", methods=["POST"])
def next_track():
    """
    API endpoint to skip to the next track.
    """
    sp = _get_spotify_client()
    if not sp:
        return jsonify({"error": "Authentication failed."}), 401

    try:
        sp.next_track()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/previous", methods=["POST"])
def previous_track():
    """
    API endpoint to skip to the previous track.
    """
    sp = _get_spotify_client()
    if not sp:
        return jsonify({"error": "Authentication failed."}), 401

    try:
        sp.previous_track()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/logout")
def logout():
    """
    Route to log the user out by clearing the session.
    """
    session.clear()
    return redirect(url_for("routes.index"))