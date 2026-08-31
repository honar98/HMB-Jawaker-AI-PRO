from bot.auth.database import Database
from bot.subscription.service import (
    create_monthly_subscription,
    subscription_status,
)


class SubscriptionAPI:
    def __init__(self, database=None):
        self.db = database or Database()
        self.db.initialize()

    def create_test_subscription(self, user_id):
        subscription = create_monthly_subscription(user_id)

        self.db.connection.execute(
            """
            INSERT INTO subscriptions
            (user_id, plan, status, expires_at, created_at)
            VALUES (?, ?, ?, ?, datetime('now'))
            """,
            (
                subscription.user_id,
                subscription.plan,
                subscription.status,
                subscription.expires_at,
            ),
        )

        self.db.connection.commit()

        return subscription_status(subscription)

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

        from bot.subscription.models import Subscription

        subscription = Subscription(
            user_id=row["user_id"],
            plan=row["plan"],
            status=row["status"],
            expires_at=row["expires_at"],
        )

        return subscription_status(subscription)
