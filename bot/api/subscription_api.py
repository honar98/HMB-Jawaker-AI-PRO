from datetime import datetime, timezone

from bot.auth.database import Database
from bot.subscription.models import Subscription
from bot.subscription.service import subscription_status


class SubscriptionAPI:
    def __init__(self, database=None):
        self.db = database or Database()
        self.db.initialize()

    def get_status(self, user_id):
        row = self.db.connection.execute(
            """
            SELECT user_id, plan, status, expires_at
            FROM subscriptions
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (user_id,),
        ).fetchone()

        if row is None:
            return {
                "active": False,
                "status": "none",
            }

        subscription = Subscription(
            user_id=row["user_id"],
            plan=row["plan"],
            status=row["status"],
            expires_at=row["expires_at"],
        )

        return subscription_status(subscription)

    def activate_payment(
        self,
        user_id,
        plan,
        payment_reference,
    ):
        now = datetime.now(timezone.utc).isoformat()

        existing = self.db.connection.execute(
            """
            SELECT id
            FROM subscriptions
            WHERE payment_reference = ?
            LIMIT 1
            """,
            (payment_reference,),
        ).fetchone()

        if existing is not None:
            return False

        days = {
            "daily": 1,
            "weekly": 7,
            "monthly": 30,
        }

        if plan not in days:
            raise ValueError(
                "Invalid subscription plan"
            )

        from datetime import timedelta

        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(days=days[plan])
        ).isoformat()

        self.db.connection.execute(
            """
            INSERT INTO subscriptions
            (
                user_id,
                plan,
                status,
                expires_at,
                payment_reference,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                plan,
                "active",
                expires_at,
                payment_reference,
                now,
            ),
        )

        self.db.connection.commit()

        return True
