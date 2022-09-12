from unittest.mock import patch

import arrow
from django.db.models import Q

from api2.constants import ROOT_BUDGET_NAME, DefaultTags
from api2.models import Budget, UserInfo, Tag
from budget.utils.test import BudgetTestCase

now = arrow.get(2021, 1, 1)

SIGNAL_MODULE = "api2.signals"


class TestBudget(BudgetTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user = cls.generate_user()
        cls.budget = cls.generate_budget(user=cls.user)
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
        self.assertEqual(self.budget.balance(), 2)

    def test_children_included_in_balance(self):
        #  Hierarchy
        #     root
        #   b     c
        #  d e   f g
        b = self.generate_budget(parent=self.budget_root)
        d = self.generate_budget(parent=b)
        e = self.generate_budget(parent=b)

        c = self.generate_budget(parent=self.budget_root)
        f = self.generate_budget(parent=c)
        g = self.generate_budget(parent=c)

        leaf_budgets = [d, e, f, g]
        [self.generate_transaction(amount=1, budget=budget) for budget in leaf_budgets]

        self.assertEqual(self.budget_root.balance(), 4)
        self.assertEqual(b.balance(), 2)
        self.assertEqual(c.balance(), 2)
        [self.assertEqual(budget.balance(), 1) for budget in leaf_budgets]

    @patch("arrow.now", return_value=now)
    def test_balance_range(self, _):
        date_range = (now.shift(weeks=-1).datetime, now.datetime)
        self.generate_transaction(
            budget=self.budget, date=now.shift(months=-1).datetime, amount=100
        )
        in_range = self.generate_transaction(
            budget=self.budget, date=now.shift(days=-1).datetime, amount=200
        )
        self.assertEqual(
            self.budget.balance(Q(date__range=date_range)),
            in_range.amount,
        )

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
                    budget=budget, date=date, income=False, amount=-4
                )
                self.generate_transaction(
                    budget=budget, date=date, income=False, amount=2
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

    @patch("arrow.now", return_value=now)
    def test_calculate_income_missing_transactions(self, _):
        budget_only_income = self.generate_budget()
        budget_only_outcome = self.generate_budget()
        time_period = 6

        self.generate_transaction(
            budget=budget_only_income,
            date=now.shift(days=-1),
            amount=10_00,
            income=True,
        )
        self.generate_transaction(
            budget=budget_only_outcome,
            date=now.shift(days=-1),
            amount=-10_00,
            income=False,
        )

        budget_only_income.calculate_income_outcome(time_period=time_period, save=True)
        budget_only_outcome.calculate_income_outcome(time_period=time_period, save=True)

        budget_only_income.refresh_from_db()
        budget_only_outcome.refresh_from_db()

        self.assertEqual(
            budget_only_income.income_per_month, round(10_00 / time_period)
        )
        self.assertEqual(budget_only_income.outcome_per_month, 0)

        self.assertEqual(budget_only_outcome.income_per_month, 0)
        self.assertEqual(
            budget_only_outcome.outcome_per_month, round(-10_00 / time_period)
        )

    def test_calculate_is_node_on_save(self):
        parent = self.generate_budget(name="parent", parent=self.budget_root)
        child = self.generate_budget(parent=parent, name="child")

        self.budget_root.refresh_from_db()
        parent.refresh_from_db()
        child.refresh_from_db()
        self.assertTrue(self.budget_root.is_node)
        self.assertTrue(parent.is_node)
        self.assertFalse(child.is_node)


class TestUser(BudgetTestCase):
    @classmethod
    def setUpTestData(cls):
        # Dont start with any data
        pass

    def test_ensure_user_info_created_on_create_user(self):
        with self.assertLogs(SIGNAL_MODULE, "INFO"):
            user = self.generate_user()

        self.assertTrue(UserInfo.objects.filter(user=user).exists())

    def test_ensure_no_signals_log_on_update(self):
        user = self.generate_user()

        user.username = "something"
        with self.assertNoLogs(SIGNAL_MODULE, "INFO"):
            user.save()

    def test_ensure_root_budget_created_on_create_user(self):
        with self.assertLogs(SIGNAL_MODULE, "INFO"):
            user = self.generate_user()

        self.assertTrue(
            Budget.objects.filter(
                user=user, is_node=True, name=ROOT_BUDGET_NAME
            ).exists()
        )

    def test_ensure_tags_created_on_create_user(self):
        with self.assertLogs(SIGNAL_MODULE, "INFO"):
            user = self.generate_user()

        self.assertTrue(Tag.objects.filter(name=DefaultTags.INCOME).exists())
        self.assertTrue(
            Tag.objects.filter(user=user, name=DefaultTags.TRANSFER).exists()
        )
        self.assertTrue(
            Tag.objects.filter(user=user, name=DefaultTags.PAYCHEQUE).exists()
        )
