"""Authentication service — password hashing, session tokens, expiry."""

import secrets
from datetime import datetime, timezone

import bcrypt


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def generate_session_token() -> str:
    return secrets.token_hex(32)


def is_session_expired(expires_at: datetime) -> bool:
    return datetime.now(timezone.utc) >= expires_at
