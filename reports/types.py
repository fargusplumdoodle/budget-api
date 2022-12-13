from datetime import date
from typing import Tuple, Callable, List

import arrow
from django.db.models import QuerySet

from api2.models import Transaction
from budget.utils.models import ChoiceEnum


class TimeBucketSizeOption(ChoiceEnum):
    ONE_DAY = "one_day"
    ONE_WEEK = "one_week"
    ONE_MONTH = "one_month"
    THREE_MONTHS = "three_months"
    SIX_MONTHS = "six_months"
    ONE_YEAR = "one_year"
    ONE = "one"


TimeRange = Tuple[arrow.Arrow, arrow.Arrow]
NativeTimeRange = Tuple[date, date]
ReportGenerator = Callable[[QuerySet[Transaction], TimeRange], List[int]]
