import arrow
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from oauth2_provider.models import Application

from api2.models import User, Budget, Transaction
from budget.utils.test import BudgetTestCase


class Command(BaseCommand):
    help = "Pre-populate the test database with some commonly used objects"

    def _load_users(self):
        self.user, created = User.objects.get_or_create(
            username="dev", is_staff=True
        )
        self.user.set_password(self.user.username)
        self.user.save()
        self.stdout.write(
            f'{"CREATED" if created else "LOADED"} user "{self.user.username}" with pass "{self.user.username}"'
        )

    def _load_client(self):
        Application.objects.get_or_create(
            client_id='web-client',
            name='web-client',
            client_secret=(
                "8obfUZIyyTcwHjCcl2Fv51P1OilFsgvp8TxHsBXyTawDi0Lozr2kAIhy6Z4bjJchP32SqUzezv1N0BxO0cZ02JMK2jsNZMG6jCd8sp9ejYDvUqVW2XePshD3COCPlv"
            ),
            user=self.user,
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            redirect_uris="http://127.0.0.1:3000/auth/callback"
        )

    def _load_budgets(self):
        budgets = [
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
        for budget in budgets:
            Budget.objects.get_or_create(user=self.user, **budget)

    @staticmethod
    def _load_transactions():
        expected_transactions = 50
        now = arrow.now()
        for budget in Budget.objects.all():
            existing_transactions = Transaction.objects.count()

            if existing_transactions < expected_transactions:
                expected_transactions = expected_transactions - existing_transactions
            else:
                continue

            for x in range(expected_transactions):
                BudgetTestCase.generate_transaction(
                    budget=budget, date=now.shift(days=0 - x)
                )

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

        self.stdout.write(self.style.SUCCESS("DONE"))
