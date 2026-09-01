PLANS = {
    "daily": {
        "name": "Daily",
        "days": 1,
        "price": 2000,
        "currency": "IQD",
    },
    "weekly": {
        "name": "Weekly",
        "days": 7,
        "price": 5500,
        "currency": "IQD",
    },
    "monthly": {
        "name": "Monthly",
        "days": 30,
        "price": 15000,
        "currency": "IQD",
    },
}


def get_plans():
    return PLANS.copy()


def get_plan(plan):
    return PLANS.get(plan)
