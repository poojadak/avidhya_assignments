# REQ-API-001, REQ-API-002, NFR-RATE-001, NFR-LOG-001
# Flask Blueprint: all HTTP endpoints for the URL shortener.

from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, redirect, current_app

from .extensions import limiter
from .validators import ValidationError
from .services import (
    create_short_url,
    resolve_redirect,
    get_stats,
    NotFoundError,
    ExpiredUrlError,
    DuplicateUrlError,
    AliasConflictError,
)

url_bp = Blueprint("urls", __name__)


# ── Helper: consistent JSON envelope (REQ-API-001) ────────────────────────────

def ok(data: dict, status: int = 200):
    return jsonify({"success": True, "data": data, "error": None}), status

def err(message: str, status: int):
    return jsonify({"success": False, "data": None, "error": message}), status


# ── POST /api/shorten ─────────────────────────────────────────────────────────

@url_bp.post("/api/shorten")
@limiter.limit("60 per minute")          # NFR-RATE-001
def shorten():
    """REQ-SHORT-001, REQ-SHORT-003, REQ-VAL-001..004, REQ-EXP-001"""
    body = request.get_json(silent=True) or {}

    original_url = body.get("url", "").strip()
    if not original_url:
        return err("'url' field is required.", 422)

    custom_alias = body.get("custom_alias")
    expires_at_raw = body.get("expires_at")

    # Parse expires_at
    expires_at = None
    if expires_at_raw:
        try:
            expires_at = datetime.fromisoformat(expires_at_raw)
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
        except ValueError:
            return err("'expires_at' must be a valid ISO-8601 datetime.", 422)

    blocked = current_app.config.get("BLOCKED_DOMAINS", [])
    base_url = current_app.config.get("BASE_URL", "http://localhost:5000")

    try:
        data = create_short_url(
            original_url=original_url,
            blocked_domains=blocked,
            custom_alias=custom_alias,
            expires_at=expires_at,
            base_url=base_url,
        )
        return ok(data, 201)

    except ValidationError as exc:
        return err(str(exc), 422)
    except DuplicateUrlError as exc:
        return err(str(exc), 409)
    except AliasConflictError as exc:
        return err(str(exc), 409)
    except RuntimeError as exc:
        current_app.logger.error("Code generation failed: %s", exc)
        return err("Internal error generating short code.", 500)


# ── GET /<code>  (redirect) ───────────────────────────────────────────────────

@url_bp.get("/<string:code>")
def redirect_to_url(code: str):
    """REQ-REDIR-001, REQ-REDIR-002, REQ-REDIR-003, REQ-ANAL-001..003"""
    referrer = request.headers.get("Referer")
    try:
        original_url = resolve_redirect(code, referrer=referrer)
        return redirect(original_url, code=302)   # REQ-REDIR-001
    except NotFoundError:
        return err("Short code not found.", 404)
    except ExpiredUrlError:
        return err("URL has expired.", 410)


# ── GET /api/urls/<code>/stats ────────────────────────────────────────────────

@url_bp.get("/api/urls/<string:code>/stats")
def stats(code: str):
    """REQ-ANAL-004"""
    try:
        data = get_stats(code)
        return ok(data, 200)
    except NotFoundError:
        return err("Short code not found.", 404)


# ── Global error handlers (NFR-LOG-001) ───────────────────────────────────────

@url_bp.app_errorhandler(404)
def not_found(_e):
    return err("Resource not found.", 404)

@url_bp.app_errorhandler(405)
def method_not_allowed(_e):
    return err("Method not allowed.", 405)

@url_bp.app_errorhandler(429)
def rate_limit_exceeded(_e):
    return err("Rate limit exceeded. Try again later.", 429)

@url_bp.app_errorhandler(500)
def internal_error(exc):
    current_app.logger.exception("Unhandled error: %s", exc)
    return err("An internal server error occurred.", 500)
