from django.test import TestCase
from .models import Budget, Transaction
from django.core.management.base import CommandError
import datetime
from .helper import add_money, average, generate_transactions
from .load_scripts import load_budgets, load_transactions, invalid_csv_headers, fail
from . import Validators

BUDGET_SAMPLE_LOCATION = "docs/csv/budgets_sample.csv"
TRANSACTION_SAMPLE_LOCATION = "docs/csv/transaction_sample.csv"

BAD_BUDGETS_LOCATION = "docs/csv/bad_budgets_sample.csv"
BAD_TRANSACTION_LOCATION = "docs/csv/bad_transaction_sample.csv"

TEST_TRANSACTION_DESCRIPTION = 'test transaction, please ignore'


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
        amount = 100

        # adding 100 dollars
        transactions = add_money(amount, save=True)

        # there should be one transaction added per budget
        assert len(Transaction.objects.all()) == pre_number_of_transaction + len(all_budgets)

        for trans in transactions:
            assert trans.amount == trans.budget.percentage * amount

    def test_add_money_date(self):
        date = datetime.date(2019, 1, 1)
        trans = add_money(2, date=date)
        for x in trans:
            assert x.date == date

    def test_generate_transactions(self):
        # testing there were 10 transactions created

        start_date = datetime.datetime(2019, 10, 30)

        before_transactions = len(Transaction.objects.all())

        trans = generate_transactions(start_date, 10, 10, save=True)
        assert len(trans) == 100
        assert len(Transaction.objects.all()) == before_transactions + 100

    def test_average(self) -> None:
        # creating 2 budgets
        self.budget1, created = Budget.objects.get_or_create(name="b1", percentage=0)
        self.budget2, created = Budget.objects.get_or_create(name="b2", percentage=0)
        self.budgets = [self.budget1, self.budget2]

        # creating 1 transaction for each budget on each day
        # for the first 10 days of 2019

        self.amount_per_transaction = 10
        self.transactions = []
        self.amount_added = 0
        for x in range(1, 10):
            for budget in self.budgets:
                trans, created = Transaction.objects.get_or_create(
                    amount=self.amount_per_transaction,
                    description=TEST_TRANSACTION_DESCRIPTION,
                    budget=budget,
                    date=datetime.datetime(2019, 1, x),
                )
                self.amount_added += self.amount_per_transaction
                self.transactions.append(
                    trans
                )

        # calculating average per transaction
        self.average = 20.0

        assert self.average == average(self.transactions[0].date, self.transactions[-1].date, self.budgets)


class TestGraphBudgetHistoryValidator(TestCase):
    def test_check_parameters_valid(self):
        valid_params = {
            "start": "2019-11-6",
            "end": "2019-12-1",
            "budgets": ",".join([x.name for x in Budget.objects.all()]),
        }
        Validators.GraphBudgetHistory.check_parameters(valid_params)

    def test_check_budgets_valid(self):
        # generating throwaway budgets
        budgets = []
        for x in range(10):
            budget, created = Budget.objects.get_or_create(name=str(x), percentage=x)
            budgets.append(budget.name)

        valid_params = [",".join(budgets[:5]), ",".join(budgets[:2]), ",".join(budgets)]
        for budget in valid_params:
            Validators.GraphBudgetHistory.check_budgets(budget)

    def test_check_budgets_invalid(self):
        # generating throwaway budgets
        invalid_params = ["", "kljsldkfjlskdjflskdjfj,laskdf234235", "39gulkj,food"]
        for budget in invalid_params:
            passed = False
            try:
                Validators.GraphBudgetHistory.check_budgets(budget)
            except Validators.ValidationError:
                passed = True
            assert passed

    def test_check_parameters_invalid(self):
        invalid_params = [
            {"start": "2019-11-6", "end": "2019-12-1"},
            {
                "start": "2019-11-6",
                "budgets": ",".join([x.name for x in Budget.objects.all()]),
            },
            {
                "end": "2019-12-1",
                "budgets": ",".join([x.name for x in Budget.objects.all()]),
            },
        ]
        passed = False
        for invalid_param in invalid_params:
            try:
                Validators.GraphBudgetHistory.check_parameters(invalid_param)
            except Validators.ValidationError:
                passed = True
            assert passed

    def test_check_dates_valid(self):
        valid_dates = [
            ("2019-11-6", "2019-11-7"),
            ("2019-10-6", "2019-11-6"),
            ("2019-11-8", "2020-11-6"),
            ("2068-12-2", "2069-11-6"),
        ]
        for start, end in valid_dates:
            Validators.GraphBudgetHistory.check_dates(start, end)

    def test_check_dates_invalid(self):
        invalid_dates = [
            ("20s19-11-6", "20s19-11-7"),
            ("2012-01-6", "2019--6"),
            ("1919-1-8", "2020-11-6"),
            ("20638-12-2", "2069-11-6"),
        ]
        for start, end in invalid_dates:
            passed = False
            try:
                Validators.GraphBudgetHistory.check_dates(start, end)
            except Validators.ValidationError:
                passed = True
            assert passed
