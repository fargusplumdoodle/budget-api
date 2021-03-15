from unittest.mock import patch

import arrow

from api2.models import Budget
from budget.utils.test import BudgetTestCase

now = arrow.get(2021, 1, 1)


class TestBudget(BudgetTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user = cls.generate_user()
        cls.budget = cls.generate_budget(user=cls.user, initial_balance=1)
        cls.other_budget = cls.generate_budget(user=cls.user)

    def test_balance(self):
        """
        Account balance should not include transfers
        """
        # included
        self.generate_transaction(budget=self.budget, amount=1, transfer=False),
        self.generate_transaction(budget=self.budget, amount=1, transfer=True),

        # Not included
        self.generate_transaction(budget=self.other_budget, amount=1, transfer=True),
        self.generate_transaction(budget=self.other_budget, amount=1, transfer=False)

        # 1 initial balance + 1 non transfer transaction
        self.assertEqual(self.budget.balance(), 3)

    @patch("arrow.now", return_value=now)
    def test_calculate_income_outcome(self, _):
        for x in range(4):
            self.generate_budget()

        self.time_period = 3
        for budget in Budget.objects.all():
            for month_diff in range(self.time_period):
                date = now.shift(months=0 - month_diff)

                # income
                self.generate_transaction(
                    budget=budget, date=date, income=True, amount=1
                )
                # outcome
                self.generate_transaction(
                    budget=budget, date=date, income=False, amount=-2
                )
                # not counted
                self.generate_transaction(
                    budget=budget, date=date, income=False, amount=1
                )

        for budget in Budget.objects.all():
            budget.calculate_income_outcome(save=False)

            budget.refresh_from_db()

            self.assertIsNone(budget.income_per_month)
            self.assertIsNone(budget.outcome_per_month)

        for budget in Budget.objects.all():
            budget.calculate_income_outcome(time_period=self.time_period, save=True)

            budget.refresh_from_db()

            self.assertEqual(budget.income_per_month, 1)
            self.assertEqual(budget.outcome_per_month, -2)