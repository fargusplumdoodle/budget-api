import datetime
import random

from django.contrib.auth.models import User

from api2 import SampleData
from api2.SampleData import SAMPLE_DATA
from api2.models import Budget, Transaction


def add_income(amount: int, user: User, save=False, date=None):
    """
    For adding/subtracting money to all budgets based on their percentage attribute.

    To add money to a single budget use the admin inferface... for now.

    Example: if food gets 30% of the budget, and you were to call this function with
            amount=100, then this would create a transaction on the food budget
            for 30$

    :param amount: amount in dollars you wish to add between all budgets. If the number
                    is negative, this will subtract from all budgets the same way.
    :raises ValueError: if budgets are not balanced
    :returns list of transactions:
    """
    # ensuring budgets are balanced
    assert budgets_sum_to_one()
    assert isinstance(amount, int)

    # defaults to today
    date = datetime.date.today() if date is None else date
    added_transactions = []

    for budget in Budget.objects.filter(user=user):
        trans_amount = round(amount * budget.percentage)
        transaction = Transaction(
            amount=trans_amount,
            budget=budget,
            description=random.choice(SAMPLE_DATA),
            date=date,
        )
        if save:
            transaction.save()

        added_transactions.append(transaction)

    return added_transactions


def budgets_sum_to_one():
    """
    So due to the way these budgets are set, there isn't a whole lot of garentee the user (me)
    is going to ensure that all of the budgets percentage attributes add up to one hundred percent.

    Here I want to refer to this as a balanced budget but I dont have the financial/mathematical
    knowledge to be confident when saying that.

    return true if budgets sum to one hundred percent
    """
    total = 0

    for budget in Budget.objects.all():
        total += budget.percentage

    return total == 100
