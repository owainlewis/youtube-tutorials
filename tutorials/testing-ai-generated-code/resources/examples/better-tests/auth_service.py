"""Authentication service — password hashing, session tokens, expiry.

Second implementation, driven by risk-focused tests.
Note the addition of make_session_expiry and the user_id
parameter on generate_session_token — both emerged from
writing tests that prove spec requirements.
"""

import secrets
from datetime import datetime, timedelta, timezone

import bcrypt


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def generate_session_token(user_id: int | None = None) -> str:
    """Generate a cryptographically random session token.

    The user_id parameter exists to prove that tokens are NOT
    derived from user data — the same user gets a different
    token every time.
    """
    return secrets.token_hex(32)


def make_session_expiry(duration_minutes: int = 120) -> datetime:
    """Calculate session expiry from now. Default: 2 hours."""
    return datetime.now(timezone.utc) + timedelta(minutes=duration_minutes)


def is_session_expired(expires_at: datetime) -> bool:
    return datetime.now(timezone.utc) >= expires_at
