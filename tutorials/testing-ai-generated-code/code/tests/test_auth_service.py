"""Tests for the session policy decisions described in the lesson."""

import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


CODE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CODE_DIR))

from auth_service import is_session_expired, make_session_expiry  # noqa: E402


class SessionPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 8, 4, 12, 0, tzinfo=timezone.utc)

    def test_default_session_expiry_is_120_minutes(self) -> None:
        """The documented default is applied by our policy."""
        self.assertEqual(
            make_session_expiry(now=self.now),
            self.now + timedelta(minutes=120),
        )

    def test_custom_session_duration_is_respected(self) -> None:
        """A positive caller-supplied duration overrides the default."""
        self.assertEqual(
            make_session_expiry(now=self.now, duration_minutes=30),
            self.now + timedelta(minutes=30),
        )

    def test_session_is_expired_at_the_boundary(self) -> None:
        """The exact expiry time is no longer a valid session."""
        self.assertTrue(is_session_expired(expires_at=self.now, now=self.now))

    def test_session_before_the_boundary_is_valid(self) -> None:
        """A future expiry remains valid."""
        self.assertFalse(
            is_session_expired(
                expires_at=self.now + timedelta(seconds=1),
                now=self.now,
            )
        )

    def test_non_positive_session_durations_are_rejected(self) -> None:
        """Zero and negative session lifetimes cannot be created."""
        for duration in (0, -1):
            with self.subTest(duration=duration):
                with self.assertRaisesRegex(ValueError, "must be positive"):
                    make_session_expiry(
                        now=self.now,
                        duration_minutes=duration,
                    )

    def test_naive_datetimes_are_rejected(self) -> None:
        """The policy fails clearly instead of comparing ambiguous times."""
        naive_time = datetime(2026, 8, 4, 12, 0)

        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            make_session_expiry(now=naive_time)

        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            is_session_expired(expires_at=self.now, now=naive_time)


if __name__ == "__main__":
    unittest.main()
