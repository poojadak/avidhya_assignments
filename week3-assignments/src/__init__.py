# REQ-API-001, REQ-API-002
# Flask application factory with SQLAlchemy and rate-limiting setup.

from flask import Flask
from .extensions import db, limiter
from .routes import url_bp


def create_app(config_object=None):
    """Application factory. Pass a config dict or object to override defaults."""
    app = Flask(__name__)

    # ── Default configuration ──────────────────────────────────────────────
    app.config.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///urls.db")
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)
    app.config.setdefault("SECRET_KEY", "change-me-in-production")
    app.config.setdefault("BASE_URL", "http://localhost:5000")
    # NFR-RATE-001: 60 creates per minute per IP
    app.config.setdefault("RATELIMIT_DEFAULT", "200 per minute")
    app.config.setdefault(
        "BLOCKED_DOMAINS",
        ["malware.example.com", "phishing.example.org"],
    )

    if config_object:
        if isinstance(config_object, dict):
            app.config.update(config_object)
        else:
            app.config.from_object(config_object)

    # ── Extensions ─────────────────────────────────────────────────────────
    db.init_app(app)
    limiter.init_app(app)

    # ── Blueprints ─────────────────────────────────────────────────────────
    app.register_blueprint(url_bp)

    # ── Create tables ──────────────────────────────────────────────────────
    with app.app_context():
        db.create_all()

    return app
