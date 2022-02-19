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


class ReportType(ChoiceEnum):
    BUDGET_DELTA = "budget_delta"
    TAG_DELTA = "tag_delta"
    BUDGET_BALANCE = "budget_balance"
    TAG_BALANCE = "tag_balance"
    TOTAL_NUMBER_OF_TRANSACTIONS = "total_number_of_transactions"
    INCOME_AMOUNT = "income_amount"
    TRANSFER_AMOUNT = "transfer_amount"
    TOTAL_OUTCOME_AMOUNT = "total_outcome_amount"


TimeRange = Tuple[arrow.Arrow, arrow.Arrow]
ReportGenerator = Callable[[QuerySet[Transaction, str]], List[int]]
