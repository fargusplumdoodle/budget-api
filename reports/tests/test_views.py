import arrow
from rest_framework.reverse import reverse

from api2.models import Transaction, Budget
from budget.utils.test import BudgetTestCase
from reports.time_buckets import get_time_buckets, get_report_dates
from reports.types import TimeBucketSizeOption, TimeRange

"""
Dear Isaac:
    I am sorry if you have to read through this.
    - Isaac
"""


class TestReportViewMixin:
    url: str
    time_range: TimeRange
    time_bucket_size: str

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.budget = cls.generate_budget()
        cls.time_bucket_size = TimeBucketSizeOption.ONE_MONTH.value
        cls.time_range = (arrow.get(2022, 1, 1), arrow.get(2022, 7, 1))

    def get_query_params(self, **kwargs):
        return {
            "date__gte": str(self.time_range[0].date()),
            "date__lte": str(self.time_range[1].date()),
            "time_bucket_size": self.time_bucket_size,
            **kwargs,
        }

    def test_missing_time_bucket_size_query_param(self):
        r = self.get(self.url)
        self.assertEqual(r.status_code, 400)
        self.assertIn(b"Missing", r.content)
        self.assertIn(b"time_bucket_size", r.content)

    def test_invalid_time_bucket_size_query_param(self):
        qs = self.get_query_params(time_bucket_size="invalid")
        r = self.get(self.url, query=qs)
        self.assertEqual(r.status_code, 400)
        self.assertIn(b"Invalid", r.content)
        self.assertIn(b"time_bucket_size", r.content)

    def test_invalid_date_gte_query_param(self):
        qs = self.get_query_params(date__gte="invalid")
        r = self.get(self.url, query=qs)
        self.assertEqual(r.status_code, 400)
        self.assertIn(b"valid", r.content)
        self.assertIn(b"date__gte", r.content)

    def test_invalid_date_lte_query_param(self):
        qs = self.get_query_params(date__lte="invalid")
        r = self.get(self.url, query=qs)
        self.assertEqual(r.status_code, 400)
        self.assertIn(b"valid", r.content)
        self.assertIn(b"date__lte", r.content)


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
        qp = self.get_query_params()

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
        qp = self.get_query_params(
            time_bucket_size=TimeBucketSizeOption.SIX_MONTHS.value
        )
        r = self.get(self.url, query=qp)
        self.assertEqual(r.status_code, 200)
        data = r.json()

        expected_data = {
            "dates": ["2022-01-01", "2022-07-03", "2023-01-01"],
            "data": [183, 182, 1],
        }

        self.assertEqual(data, expected_data)

    def test_transaction_counts_one(self):
        qp = self.get_query_params(time_bucket_size=TimeBucketSizeOption.ONE.value)

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
        [cls.generate_budget() for _ in range(4)]
        cls.time_bucket_size = TimeBucketSizeOption.ONE_MONTH.value
        cls.time_range = (arrow.get(2022, 1, 1), arrow.get(2022, 7, 1))
        cls.buckets = get_time_buckets(cls.time_range, cls.time_bucket_size)

        cls.budgets = Budget.objects.all()
        for bucket in cls.buckets:
            for budget in cls.budgets:
                cls.generate_transaction(budget, date=bucket[0].date(), amount=-100)
                cls.generate_transaction(budget, date=bucket[0].date(), amount=50)

    def test(self):
        qp = self.get_query_params()

        r = self.get(self.url, query=qp)
        self.assertEqual(r.status_code, 200)
        data = r.json()["data"]
        self.assertLengthEqual(data, 6)

        for budget in self.budgets:
            self.assertEqual(data[str(budget.id)], [-50, -50, -50, -50, -50, -50])


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
        qp = self.get_query_params()

        r = self.get(self.url, query=qp)
        self.assertEqual(r.status_code, 200)
        data = r.json()["data"]

        for tag in self.tags:
            self.assertEqual(data[str(tag.id)], [-50, -50, -50, -50, -50, -50])


class TestIncome(TestReportViewMixin, BudgetTestCase):
    url = reverse("reports:income-list")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.time_bucket_size = TimeBucketSizeOption.ONE.value
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
        qp = self.get_query_params()

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
        cls.time_bucket_size = TimeBucketSizeOption.ONE.value
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
        qp = self.get_query_params()

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
        cls.time_bucket_size = TimeBucketSizeOption.ONE.value
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
        qp = self.get_query_params()

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
        [cls.generate_budget() for _ in range(4)]
        cls.time_bucket_size = TimeBucketSizeOption.ONE_MONTH.value
        cls.time_range = (arrow.get(2022, 1, 1), arrow.get(2022, 7, 1))
        cls.buckets = get_time_buckets(cls.time_range, cls.time_bucket_size)
        cls.expected_bucket_values = [550, 500, 450, 400, 350, 300]

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
        qp = self.get_query_params()
        r = self.get(self.url, query=qp)
        self.assertEqual(r.status_code, 200)
        data = r.json()["data"]
        self.assertLengthEqual(data, 6)

        for budget in self.budgets:
            self.assertEqual(data[str(budget.id)], self.expected_bucket_values)

    def test_only_show_some_budgets(self):
        qp = self.get_query_params(budget__includes=self.budget.id)
        r = self.get(self.url, query=qp)
        self.assertEqual(r.status_code, 200)
        data = r.json()["data"]

        self.assertLengthEqual(data, 1)
        self.assertEqual(data[str(self.budget.id)], self.expected_bucket_values)


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
        qp = self.get_query_params()

        r = self.get(self.url, query=qp)
        self.assertEqual(r.status_code, 200)
        data = r.json()["data"]

        for tag in self.tags:
            self.assertEqual(data[str(tag.id)], [550, 500, 450, 400, 350, 300])
