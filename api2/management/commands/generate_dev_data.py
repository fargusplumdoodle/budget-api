import random

import arrow
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from oauth2_provider.models import Application

from api2.models import User, Budget, Transaction, Tag
from budget.utils.test import BudgetTestCase
from cron.jobs.update_tag_stats import UpdateTagStats


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
    TAGS = [
        "car",
        "bike",
        "gas",
        "restaurant",
        "groceries",
        "bouldering",
        "income",
        "transfer",
        "laundry",
        "rent",
        "alcohol",
        "weed",
        "utilities",
        "student loan",
        "streaming services",
        "music",
        "organ",
        "guitar",
        "phone bill",
        "government cheques",
        "internet",
        "power",
        "household supplies",
        "GDrive",
        "isaacthiessen.ca",
        "Backpacking",
        "gift",
        "ICBC",
        "trips",
        "parking",
        "tutoring",
        "video games",
        "garden",
        "bank",
        "mtg",
        "books",
        "donation",
        "social",
        "health",
        "credit card fees",
        "tools",
        "circuitry",
        "dental",
        "plane",
        "aws",
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
        Application.objects.filter(client_id="web-client").delete()
        Application.objects.create(
            client_id="web-client",
            name="web-client",
            client_secret=(
                "8obfUZIyyTcwHjCcl2Fv51P1OilFsgvp8TxHs"
                "BXyTawDi0Lozr2kAIhy6Z4bjJchP32SqUzezv1"
                "N0BxO0cZ02JMK2jsNZMG6jCd8sp9ejYDvUqVW2XePshD3COCPlv"
            ),
            user=User.objects.get(username=self.USERNAME),
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            redirect_uris=(
                "http://127.0.0.1:3000/auth/callback "
                "http://localhost:3000/auth/callback "
                "http://127.0.0.1:8000/auth/callback "
            ),
        )

    def _load_budgets(self):
        for budget in self.BUDGETS:
            Budget.objects.get_or_create(
                user=User.objects.get(username=self.USERNAME), **budget
            )

    def _load_tags(self):
        for tag in self.TAGS:
            Tag.objects.get_or_create(
                user=User.objects.get(username=self.USERNAME), name=tag
            )

    @classmethod
    def _load_transactions(cls):
        now = arrow.now()
        tags = Tag.objects.all()
        for budget in Budget.objects.all():
            existing_transactions = Transaction.objects.filter(
                budget=budget, prediction=False
            ).count()

            if existing_transactions < cls.EXPECTED_TRANSACTIONS:
                expected_transactions = (
                    cls.EXPECTED_TRANSACTIONS - existing_transactions
                )
            else:
                continue

            for x in range(expected_transactions):
                income = random.choice([True, False, False, False])
                amount = random.choice(list(range(100)))
                tag = random.choice(tags)
                BudgetTestCase.generate_transaction(
                    budget=budget,
                    date=now.shift(days=0 - x),
                    amount=amount + 400 if income else 0 - amount,
                    income=income,
                    tags=[tag],
                )

    @staticmethod
    def _calculate_income_outcome():
        for budget in Budget.objects.all():
            budget.calculate_income_outcome(save=True)

    @staticmethod
    def _update_tag_rankings():
        UpdateTagStats().run()

    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stderr.write(
                self.style.ERROR("Refusing to create dev data in production")
            )
            raise CommandError(-1)

        self._load_users()
        self._load_client()
        self._load_budgets()
        self._load_tags()
        self._load_transactions()
        self._calculate_income_outcome()
        self._update_tag_rankings()

        self.stdout.write(self.style.SUCCESS("DONE"))
