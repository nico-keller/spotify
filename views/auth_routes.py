from flask import Blueprint, redirect, request, session, url_for
from services.spotify_client import SpotifyClient

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login")
def login():
    sp_client = SpotifyClient()
    return redirect(sp_client.get_auth_url())

@auth_bp.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Authorization failed", 400

    sp_client = SpotifyClient()
    sp_client.exchange_code_for_token(code)
    return redirect(url_for('dashboard.overview'))

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('auth.login'))