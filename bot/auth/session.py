import hashlib
import secrets
from datetime import datetime, timedelta, timezone


SESSION_DAYS = 30


class SessionManager:
    def __init__(self):
        self._sessions = {}

    def create(self, user_id):
        token = secrets.token_urlsafe(32)

        token_hash = hashlib.sha256(
            token.encode("utf-8")
        ).hexdigest()

        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(days=SESSION_DAYS)
        )

        self._sessions[token_hash] = {
            "user_id": user_id,
            "expires_at": expires_at,
        }

        return token

    def get_user_id(self, token):
        if not token:
            return None

        token_hash = hashlib.sha256(
            token.encode("utf-8")
        ).hexdigest()

        session = self._sessions.get(token_hash)

        if session is None:
            return None

        if session["expires_at"] <= datetime.now(
            timezone.utc
        ):
            del self._sessions[token_hash]
            return None

        return session["user_id"]

    def revoke(self, token):
        if not token:
            return

        token_hash = hashlib.sha256(
            token.encode("utf-8")
        ).hexdigest()

        self._sessions.pop(token_hash, None)
