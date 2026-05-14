# REQ-SHORT-001, REQ-SHORT-002, REQ-ANAL-001, REQ-ANAL-002, REQ-ANAL-003
# REQ-EXP-001, REQ-EXP-002
# SQLAlchemy ORM model for stored URL records.

from datetime import datetime, timezone
from .extensions import db


class UrlRecord(db.Model):
    """Stores every shortened URL and its analytics metadata."""

    __tablename__ = "url_records"

    # ── Primary key ────────────────────────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # ── Core fields ────────────────────────────────────────────────────────
    # REQ-SHORT-001: unique 6-char code
    short_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    original_url = db.Column(db.Text, nullable=False)

    # ── Analytics ──────────────────────────────────────────────────────────
    # REQ-ANAL-001: click counter
    click_count = db.Column(db.Integer, default=0, nullable=False)
    # REQ-ANAL-002: last access time
    last_accessed = db.Column(db.DateTime(timezone=True), nullable=True)
    # REQ-ANAL-003: last referrer
    referrer = db.Column(db.String(2048), nullable=True)

    # ── Lifecycle ──────────────────────────────────────────────────────────
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    # REQ-EXP-001: optional expiry
    expires_at = db.Column(db.DateTime(timezone=True), nullable=True)
    # Soft-delete flag
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # ── Helpers ────────────────────────────────────────────────────────────
    def is_expired(self) -> bool:
        """REQ-EXP-002: Evaluate expiry at access time.
        SQLite stores datetimes as naive strings; we normalise to UTC before comparing.
        """
        if self.expires_at is None:
            return False
        exp = self.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) > exp

    def to_short_dict(self, base_url: str) -> dict:
        return {
            "short_code": self.short_code,
            "short_url": f"{base_url}/{self.short_code}",
            "original_url": self.original_url,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }

    def to_stats_dict(self) -> dict:
        return {
            "short_code": self.short_code,
            "original_url": self.original_url,
            "click_count": self.click_count,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "referrer": self.referrer,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }

    def __repr__(self):
        return f"<UrlRecord {self.short_code} → {self.original_url[:40]}>"
