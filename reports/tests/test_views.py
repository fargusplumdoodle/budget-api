import arrow
from rest_framework.reverse import reverse

from api2.models import Transaction, Budget
from budget.utils.test import BudgetTestCase
from reports.time_buckets import get_time_buckets, get_report_dates
from reports.types import TimeBucketSizeOption


"""
Dear Isaac:
    I am sorry if you have to read through this.
    - Isaac
"""


class TestReportViewMixin:
    url: str

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.budget = cls.generate_budget()

    def test_missing_time_bucket_size_query_param(self):
        r = self.get(self.url)
        self.assertEqual(r.status_code, 400)
        self.assertIn(b"Missing", r.content)
        self.assertIn(b"time_bucket_size", r.content)

    def test_invalid_time_bucket_size_query_param(self):
        r = self.get(self.url, query={"time_bucket_size": "invalid"})
        self.assertEqual(r.status_code, 400)
        self.assertIn(b"Invalid", r.content)
        self.assertIn(b"time_bucket_size", r.content)


class TestTransactionCounts(TestReportViewMixin, BudgetTestCase):
    url = reverse("reports:transaction_counts-list")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.time_bucket_size = TimeBucketSizeOption.ONE_DAY.value
        cls.time_range = (arrow.get(2022, 1, 1), arrow.get(2023, 1, 1))
        cls.buckets = get_time_buckets(cls.time_range, cls.time_bucket_size)

        for bucket in cls.buckets:
            cls.generate_transaction(cls.budget, amount=0, date=bucket[0])

    def test_transaction_counts_one_day(self):
        qp = {"time_bucket_size": TimeBucketSizeOption.ONE_DAY.value}

        r = self.get(self.url, query=qp)
        self.assertEqual(r.status_code, 200)
        data = r.json()

        self.assertEqual(data["dates"], get_report_dates(self.buckets))
        self.assertLengthEqual(data["dates"], 366)
        self.assertLengthEqual(data["data"], 366)

        for value in data["data"]:
            # We created one transaction each day
            self.assertEqual(value, 1)

    def test_transaction_counts_six_months(self):
        qp = {"time_bucket_size": TimeBucketSizeOption.SIX_MONTHS.value}

        r = self.get(self.url, query=qp)
        self.assertEqual(r.status_code, 200)
        data = r.json()

        expected_data = {
            "dates": ["2022-01-01", "2022-07-03", "2023-01-01"],
            "data": [183, 182, 1],
        }

        self.assertEqual(data, expected_data)

    def test_transaction_counts_one(self):
        qp = {"time_bucket_size": TimeBucketSizeOption.ONE.value}

        r = self.get(self.url, query=qp)
        self.assertEqual(r.status_code, 200)
        data = r.json()

        expected_data = {
            "dates": ["2022-01-01"],
            "data": [Transaction.objects.count()],
        }

        self.assertEqual(data, expected_data)


class TestBudgetDelta(TestReportViewMixin, BudgetTestCase):
    url = reverse("reports:budget_delta-list")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        [cls.generate_budget() for _ in range(5)]
        cls.time_bucket_size = TimeBucketSizeOption.ONE_MONTH.value
        cls.time_range = (arrow.get(2022, 1, 1), arrow.get(2022, 7, 1))
        cls.buckets = get_time_buckets(cls.time_range, cls.time_bucket_size)

        cls.budgets = Budget.objects.all()
        for bucket in cls.buckets:
            for budget in cls.budgets:
                cls.generate_transaction(budget, date=bucket[0].date(), amount=-100)
                cls.generate_transaction(budget, date=bucket[0].date(), amount=50)

    def test(self):
        qp = {"time_bucket_size": self.time_bucket_size}

        r = self.get(self.url, query=qp)
        self.assertEqual(r.status_code, 200)
        data = r.json()["data"]
        self.assertLengthEqual(data, 6)

        for value in data:
            for budget in self.budgets:
                self.assertEqual(value[budget.name], -50)


class TestTagDelta(TestReportViewMixin, BudgetTestCase):
    url = reverse("reports:tag_delta-list")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.time_bucket_size = TimeBucketSizeOption.ONE_MONTH.value
        cls.time_range = (arrow.get(2022, 1, 1), arrow.get(2022, 7, 1))
        cls.buckets = get_time_buckets(cls.time_range, cls.time_bucket_size)

        cls.tags = [cls.generate_tag() for _ in range(5)]
        for bucket in cls.buckets:
            for tag in cls.tags:
                cls.generate_transaction(
                    cls.budget, tags=[tag], date=bucket[0].date(), amount=-100
                )
                cls.generate_transaction(
                    cls.budget, tags=[tag], date=bucket[0].date(), amount=50
                )

    def test(self):
        qp = {"time_bucket_size": self.time_bucket_size}

        r = self.get(self.url, query=qp)
        self.assertEqual(r.status_code, 200)
        data = r.json()["data"]
        self.assertLengthEqual(data, 6)

        for value in data:
            for tag in self.tags:
                self.assertEqual(value[tag.name], -50)


class TestIncome(TestReportViewMixin, BudgetTestCase):
    url = reverse("reports:income-list")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.time_range = (arrow.get(2022, 1, 1), arrow.get(2022, 7, 1))

        cls.generate_transaction(
            cls.budget, date=arrow.get(2022, 1, 1), income=True, amount=100
        )
        cls.generate_transaction(
            cls.budget, date=arrow.get(2022, 2, 1), income=True, amount=100
        )
        cls.generate_transaction(
            cls.budget, date=arrow.get(2022, 1, 1), income=False, amount=100
        )

    def test(self):
        qp = {"time_bucket_size": TimeBucketSizeOption.ONE.value}

        r = self.get(self.url, query=qp)
        self.assertEqual(r.status_code, 200)
        data = r.json()["data"]
        self.assertLengthEqual(data, 1)

        self.assertEqual(data[0], 200)


class TestTransfer(TestReportViewMixin, BudgetTestCase):
    url = reverse("reports:transfer-list")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.time_range = (arrow.get(2022, 1, 1), arrow.get(2022, 7, 1))

        cls.generate_transaction(
            cls.budget, date=arrow.get(2022, 1, 1), transfer=True, amount=100
        )
        cls.generate_transaction(
            cls.budget, date=arrow.get(2022, 2, 1), transfer=True, amount=100
        )
        cls.generate_transaction(
            cls.budget, date=arrow.get(2022, 1, 1), transfer=False, amount=100
        )

    def test(self):
        qp = {"time_bucket_size": TimeBucketSizeOption.ONE.value}

        r = self.get(self.url, query=qp)
        self.assertEqual(r.status_code, 200)
        data = r.json()["data"]
        self.assertLengthEqual(data, 1)

        self.assertEqual(data[0], 200)


class TestOutcomeReport(TestReportViewMixin, BudgetTestCase):
    url = reverse("reports:outcome-list")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.time_range = (arrow.get(2022, 1, 1), arrow.get(2022, 7, 1))

        cls.generate_transaction(cls.budget, date=arrow.get(2022, 1, 1), amount=-100)
        cls.generate_transaction(cls.budget, date=arrow.get(2022, 2, 1), amount=50)
        cls.generate_transaction(
            cls.budget, date=arrow.get(2022, 1, 1), transfer=True, amount=100
        )
        cls.generate_transaction(
            cls.budget, date=arrow.get(2022, 1, 1), income=True, amount=100
        )

    def test(self):
        qp = {"time_bucket_size": TimeBucketSizeOption.ONE.value}

        r = self.get(self.url, query=qp)
        self.assertEqual(r.status_code, 200)
        data = r.json()["data"]
        self.assertLengthEqual(data, 1)

        self.assertEqual(data[0], -50)


class TestBudgetBalanceReport(TestReportViewMixin, BudgetTestCase):
    url = reverse("reports:budget_balance-list")

    """
    Dear Isaac:
        I am sorry if you have to read through this.
        - Isaac
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        [cls.generate_budget() for _ in range(5)]
        cls.time_bucket_size = TimeBucketSizeOption.ONE_MONTH.value
        cls.time_range = (arrow.get(2022, 1, 1), arrow.get(2022, 7, 1))
        cls.buckets = get_time_buckets(cls.time_range, cls.time_bucket_size)

        cls.budgets = Budget.objects.all()
        for bucket in cls.buckets:
            for budget in cls.budgets:
                # Initial Transactions outside time range
                cls.generate_transaction(budget, date=arrow.get(2020, 1, 1), amount=100)

                # In time range
                cls.generate_transaction(budget, date=bucket[0], amount=-50)
                cls.generate_transaction(budget, date=bucket[0], income=True, amount=50)
                cls.generate_transaction(budget, date=bucket[0], amount=-50)

    def test(self):
        qp = {
            "time_bucket_size": self.time_bucket_size,
            "date__gte": self.time_range[0].date(),
            "date__lte": self.time_range[1].date(),
        }

        r = self.get(self.url, query=qp)
        self.assertEqual(r.status_code, 200)
        data = r.json()["data"]
        self.assertLengthEqual(data, 6)

        expected_balance = 600
        for value in data:
            # We lose 50 per time period
            expected_balance -= 50

            for balance in value.values():
                self.assertEqual(balance, expected_balance)

            self.assertEqual(
                set(value.keys()), {budget.name for budget in self.budgets}
            )


class TestTagBalanceReport(TestReportViewMixin, BudgetTestCase):
    url = reverse("reports:tag_balance-list")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.time_bucket_size = TimeBucketSizeOption.ONE_MONTH.value
        cls.time_range = (arrow.get(2022, 1, 1), arrow.get(2022, 7, 1))
        cls.buckets = get_time_buckets(cls.time_range, cls.time_bucket_size)

        cls.tags = [cls.generate_tag() for _ in range(5)]
        for bucket in cls.buckets:
            for tag in cls.tags:
                # Initial Transactions outside time range
                cls.generate_transaction(
                    cls.budget, tags=[tag], date=arrow.get(2020, 1, 1), amount=100
                )

                # In time range
                cls.generate_transaction(
                    cls.budget, tags=[tag], date=bucket[0], amount=-50
                )
                cls.generate_transaction(
                    cls.budget, tags=[tag], date=bucket[0], income=True, amount=50
                )
                cls.generate_transaction(
                    cls.budget, tags=[tag], date=bucket[0], amount=-50
                )

    def test(self):
        qp = {
            "time_bucket_size": self.time_bucket_size,
            "date__gte": self.time_range[0].date(),
            "date__lte": self.time_range[1].date(),
        }

        r = self.get(self.url, query=qp)
        self.assertEqual(r.status_code, 200)
        data = r.json()["data"]
        self.assertLengthEqual(data, 6)

        expected_balance = 600
        for value in data:
            # We lose 50 per time period
            expected_balance -= 50

            for balance in value.values():
                self.assertEqual(balance, expected_balance)

            self.assertEqual(set(value.keys()), {tag.name for tag in self.tags})
