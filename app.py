from flask import Flask, redirect, url_for, session
from config import Config
from views.auth_routes import auth_bp
from views.dashboard_routes import dashboard_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)

    @app.route("/")
    def index():
        if "token_info" in session:
            return redirect(url_for("dashboard.overview"))
        return redirect(url_for("auth.login"))

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(port=8888, debug=True)
