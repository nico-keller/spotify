# views/dashboard_routes.py
# Inspo:
# https://stats.fm/keller-nicolas

from flask import Blueprint, request, render_template, jsonify, g
from utils.decorators import spotify_required
from utils.response import api_error, api_success
from collections import Counter

dashboard_bp = Blueprint("dashboard", __name__)


def get_time_range(term):
    """Map user-friendly terms to Spotify API time ranges"""
    time_ranges = {
        '4_weeks': 'short_term',
        '6_months': 'medium_term',
        'lifetime': 'long_term'
    }
    return time_ranges.get(term, 'medium_term')  # Default to 6 months


def extract_top_genres(top_artists, limit=10):
    """Extract and count genres from top artists since Spotify doesn't have a direct top genres endpoint"""
    all_genres = []
    for artist in top_artists:
        all_genres.extend(artist.get('genres', []))

    # Count genre frequency and return top genres
    genre_counts = Counter(all_genres)
    return [{'name': genre, 'count': count} for genre, count in genre_counts.most_common(limit)]


@dashboard_bp.route("/overview")
@spotify_required
def overview():
    sp = g.spotify
    # Get term from query parameters, default to 6_months
    term = request.args.get('term', '6_months')
    time_range = get_time_range(term)

    try:
        user_profile = sp.me()
        top_artists = sp.current_user_top_artists(limit=50, time_range=time_range)['items']
        top_tracks = sp.current_user_top_tracks(limit=50, time_range=time_range)['items']
        playlists = sp.current_user_playlists(limit=20)['items']
        recently_played = sp.current_user_recently_played(limit=10)['items']

        # Extract top genres from top artists
        top_genres = extract_top_genres(top_artists, limit=15)

        return render_template(
            "overview.html",
            user_profile=user_profile,
            playlists=playlists,
            top_artists=top_artists,
            top_tracks=top_tracks,
            recently_played=recently_played,
            top_genres=top_genres,
            current_term=term
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


@dashboard_bp.route("/player/play", methods=["POST"])
@spotify_required
def play():
    return _control_playback("start_playback")


@dashboard_bp.route("/player/pause", methods=["POST"])
@spotify_required
def pause():
    return _control_playback("pause_playback")


@dashboard_bp.route("/player/next", methods=["POST"])
@spotify_required
def next_track():
    return _control_playback("next_track")


@dashboard_bp.route("/player/previous", methods=["POST"])
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