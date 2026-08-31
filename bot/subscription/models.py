from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class Subscription:
    user_id: str
    plan: str
    status: str
    expires_at: str | None = None

    def is_active(self):
        if self.status != "active":
            return False

        if not self.expires_at:
            return False

        try:
            expires = datetime.fromisoformat(
                self.expires_at
            )
        except ValueError:
            return False

        return expires > datetime.now(timezone.utc)
