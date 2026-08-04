"""Session expiry policy used by the testing tutorial."""

from datetime import datetime, timedelta


DEFAULT_SESSION_MINUTES = 120


def make_session_expiry(
    *,
    now: datetime,
    duration_minutes: int = DEFAULT_SESSION_MINUTES,
) -> datetime:
    """Return a timezone-aware session expiry for a positive duration."""
    _require_timezone(now)
    if duration_minutes <= 0:
        raise ValueError("duration_minutes must be positive")

    return now + timedelta(minutes=duration_minutes)


def is_session_expired(*, expires_at: datetime, now: datetime) -> bool:
    """Return whether a session has reached or passed its expiry time."""
    _require_timezone(expires_at)
    _require_timezone(now)
    return now >= expires_at


def _require_timezone(value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("datetime values must be timezone-aware")
