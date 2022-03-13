import random
from reports.types import NativeTimeRange, TimeRange


def toNativeTimeRange(range: TimeRange) -> NativeTimeRange:
    return (range[0].datetime, range[1].datetime)


def daysBetween(range: TimeRange) -> int:
    return abs((range[1] - range[0]).days)


def roll(probability: float) -> bool:
    assert 0 < probability <= 1, probability

    i = random.randint(0, 100) / 100
    return i <= probability
