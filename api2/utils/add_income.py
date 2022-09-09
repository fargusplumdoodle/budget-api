import datetime

import arrow
from django.contrib.auth.models import User

from api2.constants import INCOME_TAG_NAME, ROOT_BUDGET_NAME
from api2.models import Budget, Transaction, Tag


def add_income(user: User, date=None):
    """
    Add allocated funds from Root to each budget
    """

    date = arrow.now() if date is None else arrow.get(date)
    root_budget, _ = Budget.objects.get_or_create(name=ROOT_BUDGET_NAME, user=user)
    income_tag, _ = Tag.objects.get_or_create(name=INCOME_TAG_NAME, user=user)

    for budget in Budget.objects.filter(user=user, monthly_allocation__gt=0):
        budget_income_trans = Transaction.objects.create(
            amount=abs(budget.monthly_allocation),
            description="Monthly Income",
            budget=budget,
            date=date.date(),
            income=True,
            transfer=False,
            prediction=False,
        )
        budget_income_trans.tags.set([income_tag])

        root_income_trans = Transaction.objects.create(
            amount=0 - abs(budget.monthly_allocation),
            description=f"Monthly Income: ${budget.name}",
            budget=root_budget,
            date=date.date(),
            income=True,
            transfer=False,
            prediction=False,
        )
        root_income_trans.tags.set([income_tag])

