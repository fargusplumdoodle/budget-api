import arrow
from django.contrib.auth.models import User

from api2.models import Budget, Transaction


def generate_user(**kwargs):
    defaults = {"username": f"user_{User.objects.count():07}"}
    defaults.update(kwargs)
    return User.objects.create(**defaults)


def generate_budget(**kwargs):
    defaults = {
        "name": f"budget_{Budget.objects.count():07}",
        "percentage": 0,
        "initial_balance": 0,
    }
    if "user" not in kwargs:
        defaults["user"] = generate_user()

    defaults.update(kwargs)
    return Budget.objects.create(**defaults)


def generate_transaction(budget: Budget, **kwargs):
    num_transactions = Transaction.objects.count()
    defaults = {
        "amount": num_transactions * 100,
        "description": f"trans: {num_transactions}",
        "budget": budget,
        "date": arrow.now().datetime,
        "income": False,
        "transfer": False,
    }
    defaults.update(kwargs)
    return Transaction.objects.create(**defaults)
