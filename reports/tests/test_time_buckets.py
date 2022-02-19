import arrow

from budget.utils.test import BudgetTestCase
from reports.time_buckets import one_day, one, get_time_buckets_by_day_delta


class TestTimeBuckets(BudgetTestCase):
    def test_one_day(self):
        start_date = arrow.get(2022, 1, 1)
        end_date = arrow.get(2022, 2, 1)

        ranges = one_day(start_date, end_date)

        for start, end in ranges:
            self.assertEqual(start, end)

        self.assertLengthEqual(ranges, 32)

    def test_time_frame_less_than_delta(self):
        # difference of 31 days
        start_date = arrow.get(2022, 1, 1)
        end_date = arrow.get(2022, 2, 1)

        ranges = get_time_buckets_by_day_delta(start_date, end_date, 100)

        self.assertEqual(ranges, [(start_date, end_date)])

    def test_one(self):
        start_date = arrow.get(2022, 1, 1)
        end_date = arrow.get(2022, 2, 1)

        self.assertEqual(one(start_date, end_date), [(start_date, end_date)])

    def test_one_week(self):
        start_date = arrow.get(2022, 1, 1)
        end_date = arrow.get(2022, 2, 1)

        ranges = get_time_buckets_by_day_delta(start_date, end_date, 7)

        expected_ranges = [
            (start_date, arrow.get(2022, 1, 8)),
            (arrow.get(2022, 1, 9), arrow.get(2022, 1, 15)),
            (arrow.get(2022, 1, 16), arrow.get(2022, 1, 22)),
            (arrow.get(2022, 1, 23), arrow.get(2022, 1, 29)),
            (arrow.get(2022, 1, 30), end_date),
        ]

        self.assertEqual(ranges, expected_ranges)

    def test_one_month(self):
        start_date = arrow.get(2022, 1, 15)
        end_date = arrow.get(2022, 3, 20)

        ranges = get_time_buckets_by_day_delta(start_date, end_date, 31)

        expected_ranges = [
            (start_date, arrow.get(2022, 2, 15)),
            (arrow.get(2022, 2, 16), arrow.get(2022, 3, 18)),
            (arrow.get(2022, 3, 19), end_date),
        ]

        self.assertEqual(ranges, expected_ranges)
