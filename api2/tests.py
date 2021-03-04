import random

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from api.models import Budget as Budget1, Transaction as Transaction1
from api2.models import Budget as Budget2, Transaction as Transaction2
from api2.SampleData import SAMPLE_DATA
from api2.management.commands.generate_transactions import (
    Command as GenerateTransactions,
)
from api2.management.commands.migrate_v1_to_v2 import Command as V1_to_V2
from datetime import date


class TestV1toV2(TestCase):
    def setUp(self):
        """
        Generating v1 budgets/transactions to copy over
        :return:
        """
        self.budgets = [
            Budget1.objects.create(name="food", percentage=0.25, initial_balance=0.0),
            Budget1.objects.create(
                name="housing", percentage=0.2523456, initial_balance=1.0
            ),
            Budget1.objects.create(
                name="test budget", percentage=0.5012324, initial_balance=100.0
            ),
        ]

        for x in range(100):
            Transaction1.objects.create(
                amount=(random.randint(10, 1000) / 100),  # random float
                description=random.choice(SAMPLE_DATA),
                budget=random.choice(self.budgets),
                date=date.today() - timezone.timedelta(days=x),
            )

        with self.settings(DEBUG=True):
            GenerateTransactions.generate_transactions(
                start_date=date(2020, 9, 8), num_paycheques=100, income=1000, save=True
            )

        self.user = User.objects.create(username="youknowwhoamirite")

    def test_convertion(self):
        # dollars, cents
        exchange_rates = [
            (10, 10_00),
            (10.123, 10_12),
            (0.623, 62),
            (0.629, 63),
        ]
        for dollars, cents in exchange_rates:
            self.assertEqual(V1_to_V2.convert_dollars_to_cents(dollars), cents)
            self.assertEqual(
                V1_to_V2.convert_cents_to_dollars(cents), round(dollars, 2)
            )

    def testBudgetsTransferredSaveFalse(self):
        V1_to_V2.v1_to_v2(user=self.user.username, save=False)

        budgets2 = Budget2.objects.all()
        transactions2 = Transaction2.objects.all()

        self.assertEqual(len(budgets2), 0)
        self.assertEqual(len(transactions2), 0)

    def testBudgetsTransferredSaveTrue(self):
        V1_to_V2.v1_to_v2(user=self.user.username, save=True)

        budgets1 = Budget1.objects.all()
        budgets2 = Budget2.objects.all()

        transactions1 = Transaction1.objects.all()
        transactions2 = Transaction2.objects.all()

        # The same number of budgets and transactions must exist
        self.assertEqual(len(budgets1), len(budgets2))
        self.assertEqual(len(transactions1), len(transactions2))

        # checking budgets first
        for budget1 in budgets1:
            budget2 = Budget2.objects.get(
                name=budget1.name,
                percentage=round(budget1.percentage * 100),
                initial_balance=V1_to_V2.convert_dollars_to_cents(
                    budget1.initial_balance
                ),
                user=self.user,
            )

            # ensuring balances are equal
            self.assertEqual(
                budget2.balance(),
                V1_to_V2.convert_dollars_to_cents(float(budget1.balance())),
            )

        for transaction1 in transactions1:
            Transaction2.objects.get(
                amount=V1_to_V2.convert_dollars_to_cents(transaction1.amount),
                description=transaction1.description,
                budget=Budget2.objects.get(name=transaction1.budget.name),
                date=transaction1.date,
            )
