from datetime import date
from typing import List, Optional, Tuple

import arrow
from django.db.models import QuerySet

from api2.models import Transaction

from .types import TimeRange, TimeBucketSizeOption


def get_time_range(transactions: QuerySet[Transaction]) -> Optional[TimeRange]:
    if transactions.count() == 0:
        return

    transactions = transactions.order_by("date")
    first_transaction = transactions.first()
    last_transaction = transactions.last()

    assert first_transaction and last_transaction
    return arrow.get(first_transaction.date), arrow.get(last_transaction.date)


def get_date_range(time_range: TimeRange) -> Tuple[date, date]:
    return (
        time_range[0].date(),
        time_range[1].date(),
    )


def get_report_dates(time_buckets: List[TimeRange]) -> List[str]:
    return [str(bucket[0].date()) for bucket in time_buckets]


def get_time_buckets(
    time_range: Optional[TimeRange], time_bucket_size: str
) -> List[TimeRange]:
    if not time_range:
        return []

    start_date = time_range[0]
    end_date = time_range[1]

    if time_bucket_size == TimeBucketSizeOption.ONE_DAY.value:
        return one_day(start_date, end_date)
    if time_bucket_size == TimeBucketSizeOption.ONE_WEEK.value:
        delta = 7
    elif time_bucket_size == TimeBucketSizeOption.ONE_MONTH.value:
        delta = 31
    elif time_bucket_size == TimeBucketSizeOption.THREE_MONTHS.value:
        delta = 365 // 4
    elif time_bucket_size == TimeBucketSizeOption.SIX_MONTHS.value:
        delta = 365 // 2
    elif time_bucket_size == TimeBucketSizeOption.ONE_YEAR.value:
        delta = 365
    else:
        return one(start_date, end_date)

    return get_time_buckets_by_day_delta(start_date, end_date, delta)


def one(start_date: arrow.Arrow, end_date: arrow.Arrow) -> List[TimeRange]:
    return [(start_date, end_date)]


def one_day(start_date: arrow.Arrow, end_date: arrow.Arrow) -> List[TimeRange]:
    diff = end_date - start_date
    ranges: List[TimeRange] = []

    for day in range(diff.days + 1):
        ranges.append((start_date.shift(days=day), start_date.shift(days=day)))

    return ranges


def get_time_buckets_by_day_delta(
    start_date: arrow.Arrow, end_date: arrow.Arrow, day_delta: int
) -> List[TimeRange]:
    diff = end_date - start_date
    ranges: List[TimeRange] = []
    for day in range(day_delta, diff.days, day_delta):
        start = ranges[-1][1].shift(days=1) if len(ranges) > 0 else start_date
        end = start_date.shift(days=day)

        ranges.append((start, end))

    mod = diff.days % day_delta
    if mod != 0:
        start = ranges[-1][1].shift(days=1) if len(ranges) > 0 else start_date
        ranges.append((start, end_date))

    return ranges
