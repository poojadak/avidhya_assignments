# REQ-VAL-001, REQ-VAL-002, REQ-VAL-003, REQ-VAL-004, NFR-SEC-002
# URL validation: scheme check, format check, blocklist check.

from urllib.parse import urlparse
import re

# Allowed custom alias pattern: 3-20 alphanumeric chars or hyphens
ALIAS_PATTERN = re.compile(r"^[a-zA-Z0-9-]{3,20}$")


class ValidationError(Exception):
    """Raised when a URL or alias fails validation."""
    def __init__(self, message: str, reason: str = "validation_error"):
        super().__init__(message)
        self.reason = reason


def validate_url(url: str, blocked_domains: list) -> None:
    """
    REQ-VAL-001: Reject non-http/https URLs.
    REQ-VAL-003: Reject URLs from blocked domains.
    NFR-SEC-002: No SSRF — we only check scheme and domain, never fetch.
    """
    if not url or not isinstance(url, str):
        raise ValidationError("URL must be a non-empty string.")

    parsed = urlparse(url.strip())

    # REQ-VAL-001: scheme must be http or https
    if parsed.scheme not in ("http", "https"):
        raise ValidationError(
            "URL must start with http:// or https://",
            reason="invalid_scheme",
        )

    # Must have a non-empty network location (host)
    if not parsed.netloc:
        raise ValidationError("URL must include a valid host.", reason="invalid_host")

    # REQ-VAL-003: blocklist check (strip www. prefix for comparison)
    hostname = parsed.hostname or ""
    bare = hostname.lower().removeprefix("www.")
    for blocked in blocked_domains:
        if bare == blocked.lower() or bare.endswith("." + blocked.lower()):
            raise ValidationError(
                f"Domain '{hostname}' is blocked.",
                reason="blocked_domain",
            )


def validate_alias(alias: str) -> None:
    """REQ-VAL-004: Custom alias format check."""
    if not ALIAS_PATTERN.match(alias):
        raise ValidationError(
            "Custom alias must be 3–20 alphanumeric characters or hyphens.",
            reason="invalid_alias",
        )
