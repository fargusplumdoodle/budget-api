from .models import Budget, Transaction
from budget.settings import DEBUG
from django.utils import timezone


def budgets_sum_to_one():
    """
    So due to the way these budgets are set, there isn't a whole lot of garentee the user (me)
    is going to ensure that all of the budgets percentage attributes add up to one.

    Here I want to refer to this as a balanced budget but I dont have the financial/mathimatical
    knowledge to be confident when saying that.

    return None if the budget is balanced or a float for the total.
    """
    total = 0

    for budget in Budget.objects.all():
        total += budget.percentage

    # returning None if budget is balanced
    if 0.999 < total < 1.0005:
        return None
    else:
        # returning total
        return total


def add_money(amount, save=False):
    """
    For adding/subtracting money to all budgets based on their percentage attribute.

    To add money to a single budget use the admin inferface... for now.

    Example: if food gets 30% of the budget, and you were to call this function with
            amount=100, then this would create a transaction with the food:

    :param amount: amount in dollars you wish to add between all budgets. If the number
                    is negative, this will subtract from all budgets the same way.
    :raises ValueError: if budgets are not balanced
    :returns list of transactions:
    """
    # ensuring budgets are balanced
    assert budgets_sum_to_one() is None

    added_transactions = []

    for budget in Budget.objects.all():
        trans_amount = amount * budget.percentage
        transaction = Transaction(
            amount=trans_amount,
            budget=budget,
            description=f"add_money: Total amount added %.2f"
            % float(amount),
        )
        if save:
            transaction.save()

        added_transactions.append(transaction)

    return added_transactions


def generate_transactions(start_date, num_paycheques, income, save=False):
    """
    Creates a bunch of transactions

    :param start_date: start date, datetime
    :param num_paycheques: number of paycheques to generate
    :param income: amount you make per 14 days
    :param save: if true we will save transactions, doesn't work in debug
    :return: list of transacitons
    """
    if not DEBUG and save:
        raise EnvironmentError("Will not generate transactions when DEBUG is True")

    budgets = Budget.objects.all()
    number_of_days_between_paychecks = 14

    transactions = []
    for x in range(-num_paycheques, 0):
        date = start_date - timezone.timedelta(days=int(number_of_days_between_paychecks * x))
        for budget in budgets:
            trans_amount = income * budget.percentage
            trans = Transaction(
                amount=trans_amount,
                budget=budget,
                description=f"generate_transactions command. Total amount added %.2f"
                            % float(income),
                date=date
            )
            # wont save unless we are in debug mode
            if save and DEBUG:
                trans.save()

            #  adding transaction to return list
            transactions.append(trans)

    # returning transacions
    return transactions










































