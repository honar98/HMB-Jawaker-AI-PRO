from datetime import datetime, timedelta, timezone

from .models import Subscription


MONTHLY_DAYS = 30


def create_monthly_subscription(user_id):
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=MONTHLY_DAYS)

    return Subscription(
        user_id=user_id,
        plan="monthly",
        status="active",
        expires_at=expires_at.isoformat(),
    )


def subscription_status(subscription):
    if subscription is None:
        return {
            "active": False,
            "status": "none",
        }

    active = subscription.is_active()

    return {
        "active": active,
        "status": (
            "active"
            if active
            else "expired"
        ),
        "plan": subscription.plan,
        "expires_at": subscription.expires_at,
    }
