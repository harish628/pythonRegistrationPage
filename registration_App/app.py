import os

from flask import Flask, jsonify, render_template
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from werkzeug.exceptions import HTTPException

from config.database import db, get_database_uri
from routes.registration_routes import registration_bp


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = get_database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # Check that a pooled connection is alive before using it.
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}

    db.init_app(app)
    app.register_blueprint(registration_bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/health")
    def health():
        return jsonify({"status": "UP"}), 200

    # ---- Error handlers: always return simple JSON, never internal details ----

    @app.errorhandler(OperationalError)
    def handle_connection_error(e):
        db.session.rollback()
        app.logger.error("Database connection failure: %s", e.__class__.__name__)
        return jsonify({"error": "Database connection failed"}), 500

    @app.errorhandler(SQLAlchemyError)
    def handle_database_error(e):
        db.session.rollback()
        app.logger.error("Database error: %s", e.__class__.__name__)
        return jsonify({"error": "A database error occurred"}), 500

    @app.errorhandler(HTTPException)
    def handle_http_error(e):
        return jsonify({"error": e.name}), e.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        app.logger.exception("Unexpected error")
        return jsonify({"error": "Internal server error"}), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(
        host=os.getenv("APP_HOST", "0.0.0.0"),
        port=int(os.getenv("APP_PORT", "5000")),
        debug=os.getenv("APP_DEBUG", "false").lower() == "true",
    )
