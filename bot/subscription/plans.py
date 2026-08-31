PLANS = {
    "daily": {
        "name": "Daily",
        "days": 1,
        "price": 2.00,
        "currency": "USD",
    },
    "weekly": {
        "name": "Weekly",
        "days": 7,
        "price": 5.50,
        "currency": "USD",
    },
    "monthly": {
        "name": "Monthly",
        "days": 30,
        "price": 15.00,
        "currency": "USD",
    },
}


def get_plans():
    return PLANS.copy()


def get_plan(plan):
    return PLANS.get(plan)
