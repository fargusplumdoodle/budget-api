from .models import Budget, Transaction


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


def add_money(amount):
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
            description=f"add_money: Total amount added %.2f" % float(amount*budget.percentage),
        )
        transaction.save()

        added_transactions.append(transaction)

    return added_transactions
