import random

import arrow
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from oauth2_provider.models import Application

from api2.models import User, Budget, Transaction
from budget.utils.test import BudgetTestCase
from .calculate_income_outcome import Command as CalculateIncomeOutcome


class Command(BaseCommand):
    help = "Pre-populate the test database with some commonly used objects"
    EXPECTED_TRANSACTIONS = 50
    BUDGETS = [
        {"name": "housing", "percentage": 41},
        {"name": "food", "percentage": 22},
        {"name": "debt", "percentage": 11},
        {"name": "transportation", "percentage": 6},
        {"name": "savings", "percentage": 6},
        {"name": "personal", "percentage": 5},
        {"name": "phone", "percentage": 3},
        {"name": "health", "percentage": 2},
        {"name": "camping", "percentage": 1},
        {"name": "server", "percentage": 1},
        {"name": "clothing", "percentage": 1},
        {"name": "charity", "percentage": 1},
    ]
    USERNAME = "dev"

    def _load_users(self):
        user, created = User.objects.get_or_create(
            username=self.USERNAME, is_staff=True
        )
        user.set_password(user.username)
        user.save()
        self.stdout.write(
            f'{"CREATED" if created else "LOADED"} user "{user.username}" with pass "{user.username}"'
        )

    def _load_client(self):
        Application.objects.get_or_create(
            client_id="web-client",
            name="web-client",
            client_secret=(
                "8obfUZIyyTcwHjCcl2Fv51P1OilFsgvp8TxHsBXyTawDi0Lozr2kAIhy6Z4bjJchP32SqUzezv1N0BxO0cZ02JMK2jsNZMG6jCd8sp9ejYDvUqVW2XePshD3COCPlv"
            ),
            user=User.objects.get(username=self.USERNAME),
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            redirect_uris="http://127.0.0.1:3000/auth/callback",
        )

    def _load_budgets(self):
        for budget in self.BUDGETS:
            Budget.objects.get_or_create(
                user=User.objects.get(username=self.USERNAME), **budget
            )

    @classmethod
    def _load_transactions(cls):
        now = arrow.now()
        for budget in Budget.objects.all():
            existing_transactions = Transaction.objects.filter(budget=budget).count()

            if existing_transactions < cls.EXPECTED_TRANSACTIONS:
                expected_transactions = (
                    cls.EXPECTED_TRANSACTIONS - existing_transactions
                )
            else:
                continue

            for x in range(expected_transactions):
                income = random.choice([True, False, False, False])
                amount = random.choice(list(range(100)))
                BudgetTestCase.generate_transaction(
                    budget=budget,
                    date=now.shift(days=0 - x),
                    amount=amount + 400 if income else 0 - amount,
                    income=income
                )

    @staticmethod
    def _calculate_income_outcome():
        for budget in Budget.objects.all():
            budget.calculate_income_outcome(save=True)

    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stderr.write(
                self.style.ERROR("Refusing to create dev data in production")
            )
            raise CommandError(-1)

        self._load_users()
        self._load_client()
        self._load_budgets()
        self._load_transactions()
        self._calculate_income_outcome()

        self.stdout.write(self.style.SUCCESS("DONE"))
