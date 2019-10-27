from .models import Budget


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
    if 0.999 < total < 1.0001:
        return None
    else:
        # returning total
        return total
