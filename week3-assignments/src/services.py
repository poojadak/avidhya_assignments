# REQ-SHORT-001, REQ-SHORT-002, REQ-SHORT-003
# REQ-REDIR-001, REQ-REDIR-002, REQ-REDIR-003
# REQ-ANAL-001, REQ-ANAL-002, REQ-ANAL-003, REQ-ANAL-004
# REQ-EXP-001, REQ-EXP-002, REQ-VAL-002
# Business-logic service layer — no Flask request/response objects here.

import random
import string
from datetime import datetime, timezone
from typing import Optional

from .extensions import db
from .models import UrlRecord
from .validators import ValidationError, validate_url, validate_alias


# ── Code Generation ───────────────────────────────────────────────────────────

CODE_ALPHABET = string.ascii_letters + string.digits  # 62 chars
CODE_LENGTH = 6
MAX_RETRIES = 5  # REQ-SHORT-002


def _generate_code() -> str:
    return "".join(random.choices(CODE_ALPHABET, k=CODE_LENGTH))


# ── Service functions ─────────────────────────────────────────────────────────

def create_short_url(
    original_url: str,
    blocked_domains: list,
    custom_alias: Optional[str] = None,
    expires_at: Optional[datetime] = None,
    base_url: str = "http://localhost:5000",
) -> dict:
    """
    REQ-SHORT-001: Accept valid URL → return short code.
    REQ-SHORT-002: Guarantee uniqueness; retry up to MAX_RETRIES.
    REQ-SHORT-003: Support custom alias.
    REQ-VAL-001/003: Delegate URL validation to validators module.
    REQ-VAL-002: Reject duplicate active URLs.
    REQ-VAL-004: Reject taken aliases.
    REQ-EXP-001: Store optional expires_at.
    """
    # ── Validate URL ──────────────────────────────────────────────────────
    validate_url(original_url, blocked_domains)  # raises ValidationError on failure

    # ── Duplicate check (REQ-VAL-002) ─────────────────────────────────────
    existing = UrlRecord.query.filter_by(
        original_url=original_url, is_active=True
    ).first()
    if existing and not existing.is_expired():
        raise DuplicateUrlError(
            "URL already shortened.", existing_code=existing.short_code
        )

    # ── Resolve short code ────────────────────────────────────────────────
    if custom_alias:
        validate_alias(custom_alias)  # REQ-VAL-004 format check
        taken = UrlRecord.query.filter_by(short_code=custom_alias).first()
        if taken:
            raise AliasConflictError("Alias already taken.")
        short_code = custom_alias
    else:
        # REQ-SHORT-002: retry loop
        short_code = None
        for _ in range(MAX_RETRIES):
            candidate = _generate_code()
            if not UrlRecord.query.filter_by(short_code=candidate).first():
                short_code = candidate
                break
        if short_code is None:
            raise RuntimeError("Could not generate unique code after retries.")

    # ── Persist ───────────────────────────────────────────────────────────
    record = UrlRecord(
        short_code=short_code,
        original_url=original_url,
        expires_at=expires_at,
    )
    db.session.add(record)
    db.session.commit()

    return record.to_short_dict(base_url)


def resolve_redirect(short_code: str, referrer: Optional[str] = None) -> str:
    """
    REQ-REDIR-001: Return original URL for a valid, active code.
    REQ-REDIR-002: Raise NotFoundError if code missing.
    REQ-REDIR-003: Raise ExpiredUrlError if expired.
    REQ-ANAL-001/002/003: Update click_count, last_accessed, referrer.
    """
    record = UrlRecord.query.filter_by(short_code=short_code, is_active=True).first()

    if record is None:
        raise NotFoundError(f"Short code '{short_code}' not found.")

    # REQ-REDIR-003 / REQ-EXP-002
    if record.is_expired():
        raise ExpiredUrlError("URL has expired.")

    # REQ-ANAL-001/002/003
    record.click_count += 1
    record.last_accessed = datetime.now(timezone.utc)
    if referrer:
        record.referrer = referrer
    db.session.commit()

    return record.original_url


def get_stats(short_code: str) -> dict:
    """REQ-ANAL-004: Return analytics stats for a short code."""
    record = UrlRecord.query.filter_by(short_code=short_code).first()
    if record is None:
        raise NotFoundError(f"Short code '{short_code}' not found.")
    return record.to_stats_dict()


# ── Domain exceptions ─────────────────────────────────────────────────────────

class NotFoundError(Exception):
    pass

class ExpiredUrlError(Exception):
    pass

class DuplicateUrlError(Exception):
    def __init__(self, message, existing_code=None):
        super().__init__(message)
        self.existing_code = existing_code

class AliasConflictError(Exception):
    pass
