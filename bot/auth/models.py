from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class User:
    user_id: str
    email: str
    password_hash: str
    created_at: str

    @classmethod
    def create(cls, user_id, email, password_hash):
        return cls(
            user_id=user_id,
            email=email.strip().lower(),
            password_hash=password_hash,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
