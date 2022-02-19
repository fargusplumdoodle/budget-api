from typing import Type

import arrow
from rest_framework.reverse import reverse

from api2.models import Transaction
from budget.utils.test import BudgetTestCase
from reports.time_buckets import get_time_buckets, get_report_dates
from reports.types import TimeBucketSizeOption


class TestReportViewMixin:
    url: str

    @classmethod
    def setUpTestData(cls: Type[BudgetTestCase]):
        super().setUpTestData()
        cls.budget = cls.generate_budget()

    def test_missing_time_bucket_size_query_param(self: BudgetTestCase):
        r = self.get(self.url)
        self.assertEqual(r.status_code, 400)
        self.assertIn(b"Missing", r.content)
        self.assertIn(b"time_bucket_size", r.content)

    def test_invalid_time_bucket_size_query_param(self: BudgetTestCase):
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
