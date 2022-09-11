from unittest import skip
from unittest.mock import patch

import arrow

from api2.custom_migrations.budget_tree.RemoveInitialBalance import (
    RemoveInitialBalance,
    INITIAL_BALANCE_TAG_NAME,
    INITIAL_BALANCE_TRANSACTION_DESCRIPTION,
)
from api2.models import Budget, Tag, Transaction
from budget.utils.test import BudgetTestCase


@skip("Migrations dont need to be tested")
class RemoveInitialBalanceTestCase(BudgetTestCase):
    migration = RemoveInitialBalance(app=None, db="default", testing=True)

    def forward(self):
        self.migration.forward()

    def test(self):
        first_day = arrow.get(2020, 1, 1).datetime
        budget = self.generate_budget(initial_balance=50)

        existing_transactions = [
            self.generate_transaction(
                budget,
                date=arrow.get(first_day).shift(days=i),
            )
            for i in range(3)
        ]

        self.forward()

        budget.refresh_from_db()

        initial_balance_tag = Tag.objects.get(
            user=self.user, name=INITIAL_BALANCE_TAG_NAME
        )
        self.assertEqual(budget.initial_balance, 0)
        self.assertTrue(
            Transaction.objects.filter(
                budget=budget,
                amount=50,
                date=first_day,
                tags=initial_balance_tag,
                description=INITIAL_BALANCE_TRANSACTION_DESCRIPTION,
            ).exists()
        )
