from api.models import Budget, Transaction
from budget.settings import DEBUG
from django.utils import timezone
import datetime


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


def add_money(amount, save=False, date=None):
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
    assert budgets_sum_to_one() is None

    # defaults to today
    date = datetime.date.today() if date is None else date
    added_transactions = []

    for budget in Budget.objects.all():
        trans_amount = amount * budget.percentage
        transaction = Transaction(
            amount=trans_amount,
            budget=budget,
            description="add_money: Total amount added %.2f" % float(amount),
            date=date,
        )
        if save:
            transaction.save()

        added_transactions.append(transaction)

    return added_transactions


def generate_transactions(start_date, num_paycheques, income, save=False):
    """
    Creates a bunch of transactions. This function is largly for testing

    Calls add_money to generate transactions, this will add num_paycheques * x where x is
    the number of budgets that exist

    :param start_date: start date, datetime
    :param num_paycheques: number of paycheques to generate
    :param income: amount you make per 14 days
    :param save: if true we will save transactions, doesn't work in debug
    :return: list of transacitons
    """
    if not DEBUG and save:
        raise EnvironmentError("Will not generate transactions when DEBUG is True")

    number_of_days_between_paychecks = 14

    # wont save unless we are in debug mode
    save = save and DEBUG

    transactions = []
    for x in range(-num_paycheques, 0):
        date = start_date - timezone.timedelta(
            days=int(number_of_days_between_paychecks * x)
        )
        transactions = transactions + add_money(income, date=date, save=save)

    # returning transacions
    return transactions


def average_per_day(start, end, budgets):
    """
    Average function:
    returns the average amount spent per day
    :param start: date, start date must be less than end date
    :param end: end date
    :param budgets: list of budget objects to get the average spent per day of
    :return: average amount spent per day
    """
    assert start < end  # start must be less than end
    days = (end - start).days

    # fixing bad input
    if days <= 0:
        return 0.0

    sum = 0
    for x in range(1, days + 2):
        date = start + datetime.timedelta(days=x)
        # this is a list of the transactions that occured on this day
        # within the specified budgets
        transactions = Transaction.objects.filter(date=date, budget__in=budgets)

        for x in transactions:
            sum += x.amount

    return round(sum / days, 2)


def get_sum_of_transactions(trans, budget=None):
    """
    :param trans: QuerySet of Transactions
    :param budget: budget to get sum for
    :return: summation of all transacions amount value
    """
    sum = 0
    if budget is not None:
        for x in trans.filter(budget=budget):
            sum += x.amount
    else:
        for x in trans:
            sum += x.amount

    return sum
