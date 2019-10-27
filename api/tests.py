from django.test import TestCase
from .models import Budget, Transaction
from django.core.management.base import CommandError
from .helper import add_money, budgets_sum_to_one
from .load_scripts import load_budgets, load_transactions, invalid_csv_headers, fail

BUDGET_SAMPLE_LOCATION = "docs/csv/budgets_sample.csv"
TRANSACTION_SAMPLE_LOCATION = "docs/csv/transaction_sample.csv"

BAD_BUDGETS_LOCATION = "docs/csv/bad_budgets_sample.csv"
BAD_TRANSACTION_LOCATION = "docs/csv/bad_transaction_sample.csv"


class TestLoadScripts(TestCase):
    def test_invalid_csv_headers(self):
        # trying valid input
        fields = ["a", "b", "c"]
        assert invalid_csv_headers(fields, fields) is None

        # trying one less field
        assert invalid_csv_headers(fields, fields.pop()) is not None

    def test_fail(self):
        passed = False
        try:
            fail("eyy")
        except CommandError:
            passed = True

        assert passed

    def test_load_budgets_invalid(self):
        passed = False
        try:
            load_budgets(BAD_BUDGETS_LOCATION, verbose=False)
        except CommandError:
            passed = True
        assert passed

    def test_load_budgets_valid(self):
        load_budgets(BUDGET_SAMPLE_LOCATION, verbose=False)

    def test_load_transactions_invalid(self):
        passed = False
        try:
            load_transactions(BAD_TRANSACTION_LOCATION)
        except CommandError:
            passed = True
        assert passed

    def test_load_transactions_valid(self):
        # loading budgets, must be done first
        load_budgets(BUDGET_SAMPLE_LOCATION, verbose=False)
        # loading transactions
        load_transactions(TRANSACTION_SAMPLE_LOCATION)


class TestHelpers(TestCase):
    def setUp(self) -> None:
        load_budgets(BUDGET_SAMPLE_LOCATION, verbose=False)
        load_transactions(TRANSACTION_SAMPLE_LOCATION)

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
        assert len(Transaction.objects.all()) == pre_number_of_transaction + len(
            all_budgets
        )

        recent_transactions = Transaction.objects.order_by("date")[::-1]

        print(recent_transactions)

    def test_budgets_sum_to_one(self):
        # TODO: THIS
        pass
