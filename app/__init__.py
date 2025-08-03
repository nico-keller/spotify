from flask import Flask
from dotenv import load_dotenv
import os


def create_app():
    """
    Application factory function. Creates and configures the Flask app.
    """
    app = Flask(__name__)

    # Load environment variables
    load_dotenv()

    # Configure the app
    app.secret_key = os.environ.get("FLASK_SECRET_KEY")
    app.config['SESSION_COOKIE_NAME'] = 'SpotifySessionCookie'

    # Import and register blueprints or routes
    from . import routes
    app.register_blueprint(routes.bp)

    return app