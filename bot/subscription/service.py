from datetime import datetime, timedelta, timezone

from .models import Subscription


PLAN_DAYS = {
    "daily": 1,
    "weekly": 7,
    "monthly": 30,
}


def create_subscription(user_id, plan):
    plan = plan.strip().lower()

    if plan not in PLAN_DAYS:
        raise ValueError("Invalid subscription plan")

    now = datetime.now(timezone.utc)

    expires_at = (
        now
        + timedelta(days=PLAN_DAYS[plan])
    )

    return Subscription(
        user_id=user_id,
        plan=plan,
        status="active",
        expires_at=expires_at.isoformat(),
    )


def create_daily_subscription(user_id):
    return create_subscription(user_id, "daily")


def create_weekly_subscription(user_id):
    return create_subscription(user_id, "weekly")


def create_monthly_subscription(user_id):
    return create_subscription(user_id, "monthly")


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
