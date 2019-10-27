from django.test import TestCase
from .models import Budget, Transaction
from django.core.management import call_command
from .helper import add_money, budgets_sum_to_one
from .management.commands.load_transactions import Command as LoadTransaction

BUDGET_SAMPLE_LOCATION = "docs/csv/budgets_sample.csv"

class TestCommands(TestCase):
    def test_validate_csv(self):
        lt = LoadTransaction()

        # trying valid input
        fields = [x for x in lt.REQUIRED_FIELDS]
        assert lt.invalid_csv_headers(fields) is None

        # trying one less field
        fields.pop()
        assert lt.invalid_csv_headers(fields) is not None


class TestHelpers(TestCase):
    def setUp(self) -> None:
        call_command('load_budgets', verbosity=0, input_csv=BUDGET_SAMPLE_LOCATION)

    def test_add_money(self):
        """
        We want to ensure that
            - a transaction is created for each budget
            - the amount on each transaction is correct
        """
        all_budgets = Budget.objects.all()
        pre_number_of_transaction = len(Transaction.objects.all())

        # adding 100 dollars
        add_money(100)

        # there should be one transaction added per budget
        assert len(Transaction.objects.all()) == pre_number_of_transaction + len(all_budgets)

        recent_transactions = Transaction.objects.order_by('date')[::-1]

        print(recent_transactions)

    def test_budgets_sum_to_one(self):
        """"""
        # TODO: THIS
