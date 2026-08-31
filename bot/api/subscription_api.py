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
