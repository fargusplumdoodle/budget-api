from typing import Dict, TYPE_CHECKING
from api2.models import Budget, Tag, Transaction
from reports.types import TimeRange
from django.db.models import Avg

from reports.utils import daysBetween, toNativeTimeRange

if TYPE_CHECKING:
    from django.db.models import QuerySet


class Predictor:
    """
    Takes:
        Analyze data time:
          - Time to take average of
        Date range to predict:
          - must be in future

    Income and transfers are not accounted for at this time
    """

    def __init__(self, analyze_range: TimeRange, prediction_range: TimeRange) -> None:
        self.analysis_range = analyze_range
        self.prediction_range = prediction_range

        self.example_transactions = Transaction.objects.filter(
            date__range=toNativeTimeRange(analyze_range)
        )

        self.analysis_start, self.analysis_end = analyze_range
        self.days_in_analysis_period = daysBetween(self.analysis_range)

        self.prediction_start, self.prediction_end = prediction_range
        self.days_in_prediction_period = daysBetween(self.prediction_range)

        self.transactions_in_analysis_period = self.example_transactions.count()

        self.average_transaction_amount = self._get_average_amount()
        self.odds_of_transaction_occurence = self._get_odds_of_transaction_occurence()
        self.unique_budgets = self._get_unique_budgets()
        self.unique_tags = self._get_unique_tags()

        self.tag_odds_distribution = self._get_tag_odds_distribution()
        self.budget_odds_distribution = self._get_budget_odds_distribution()

    def _get_average_amount(self) -> int:
        return round(self.example_transactions.aggregate(avg=Avg("amount"))["avg"])

    def _get_odds_of_transaction_occurence(self) -> float:
        return self.transactions_in_analysis_period / self.days_in_analysis_period

    def _get_unique_budgets(self) -> "QuerySet[Budget]":
        return Budget.objects.filter(
            pk__in=self.example_transactions.values_list("budget", flat=True)
        )

    def _get_unique_tags(self) -> "QuerySet[Tag]":
        return Tag.objects.filter(
            pk__in=self.example_transactions.values_list("tags", flat=True)
        )

    def _get_tag_odds_distribution(self) -> Dict[Tag, float]:
        def odds_of_tag(tag: Tag) -> float:
            return (
                self.example_transactions.filter(tags=tag).count()
                / self.transactions_in_analysis_period
            )

        return {tag: odds_of_tag(tag) for tag in self.unique_tags}

    def _get_budget_odds_distribution(self) -> Dict[Budget, float]:
        def odds_of_budget(budget: Budget) -> float:
            return (
                self.example_transactions.filter(budget=budget).count()
                / self.transactions_in_analysis_period
            )

        return {budget: odds_of_budget(budget) for budget in self.unique_budgets}
