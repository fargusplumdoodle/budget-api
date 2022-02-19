from typing import List

import arrow
from django.db.models import QuerySet

from api2.models import Transaction

from .types import TimeRange, TimeBucketSizeOption


def get_time_buckets(
    transactions: QuerySet[Transaction], time_bucket: str
) -> List[TimeRange]:
    if transactions.length == 0:
        return []

    transactions = transactions.order_by("-date")
    first_transaction = transactions.first()
    last_transaction = transactions.last()

    assert first_transaction and last_transaction
    start_date = first_transaction.date
    end_date = last_transaction.date

    if time_bucket == TimeBucketSizeOption.ONE_DAY.value:
        return one_day(start_date, end_date)
    if time_bucket == TimeBucketSizeOption.ONE_WEEK.value:
        return get_time_buckets_by_day_delta(start_date, end_date, 7)
    if time_bucket == TimeBucketSizeOption.ONE_MONTH.value:
        return get_time_buckets_by_day_delta(start_date, end_date, 31)
    if time_bucket == TimeBucketSizeOption.THREE_MONTHS.value:
        return get_time_buckets_by_day_delta(start_date, end_date, 365 // 4)
    if time_bucket == TimeBucketSizeOption.SIX_MONTHS.value:
        return get_time_buckets_by_day_delta(start_date, end_date, 365 // 2)
    if time_bucket == TimeBucketSizeOption.ONE_YEAR.value:
        return get_time_buckets_by_day_delta(start_date, end_date, 365)
    else:
        method = one

    return method(start_date, end_date)


def one(start_date: arrow.Arrow, end_date: arrow.Arrow) -> List[TimeRange]:
    return [(start_date, end_date)]


def one_day(start_date: arrow.Arrow, end_date: arrow.Arrow) -> List[TimeRange]:
    diff = end_date - start_date
    ranges: List[TimeRange] = []

    for day in range(diff.days):
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
