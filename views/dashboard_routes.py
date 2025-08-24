# views/dashboard_routes.py

from flask import Blueprint, request, render_template, jsonify, g
from utils.decorators import spotify_required
from utils.response import api_error, api_success

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/overview")
@spotify_required
def overview():
    sp = g.spotify
    try:
        user_profile = sp.me()
        playlists = sp.current_user_playlists(limit=15)['items']
        top_artists = sp.current_user_top_artists(limit=10, time_range="short_term")['items']
        top_tracks = sp.current_user_top_tracks(limit=10, time_range="short_term")['items']
        recently_played = sp.current_user_recently_played(limit=5)['items']

        return render_template(
            "overview.html",
            user_profile=user_profile,
            playlists=playlists,
            top_artists=top_artists,
            top_tracks=top_tracks,
            recently_played=recently_played
        )
    except Exception as e:
        return render_template("error.html", message=str(e))

@dashboard_bp.route("/search")
@spotify_required
def search():
    sp = g.spotify
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'track')

    if not query:
        return api_error("Query parameter 'q' is required.", 400)

    try:
        results = sp.search(q=query, type=search_type, limit=10)
        return api_success(results)
    except Exception as e:
        return api_error(str(e))

@dashboard_bp.route("/play", methods=["POST"])
@spotify_required
def play():
    return _control_playback("start_playback")

@dashboard_bp.route("/pause", methods=["POST"])
@spotify_required
def pause():
    return _control_playback("pause_playback")

@dashboard_bp.route("/next", methods=["POST"])
@spotify_required
def next_track():
    return _control_playback("next_track")

@dashboard_bp.route("/previous", methods=["POST"])
@spotify_required
def previous_track():
    return _control_playback("previous_track")

def _control_playback(action):
    sp = g.spotify
    try:
        getattr(sp, action)()
        return api_success()
    except Exception as e:
        return api_error(str(e))
