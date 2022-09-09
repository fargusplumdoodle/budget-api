import random
from typing import Dict, TYPE_CHECKING, List
from typing_extensions import TypedDict
from django.contrib.auth.models import User

from api2.constants import ROOT_BUDGET_NAME, PAYCHEQUE_TAG_NAME
from api2.models import Budget, Tag, Transaction, UserInfo
from api2.utils.add_monthly_income import add_monthly_income
from reports.constants import PREDICTION_TRANSACTION_DESCRIPTION
from reports.types import TimeRange
from django.db.models import Avg

from reports.utils import daysBetween, roll, toNativeTimeRange

if TYPE_CHECKING:
    from django.db.models import QuerySet

TagProbDistro = TypedDict("TagProbDistro", {"prob": float, "average_amount": int})
BudgetProbDistro = TypedDict(
    "BudgetProbDistro", {"prob": float, "tags": Dict[Tag, TagProbDistro]}
)
ProbabilityDistrobution = Dict[Budget, BudgetProbDistro]


class Predictor:
    """
    Creates prediction transactions based on weighted distrobution of budgets and
    tags for each budget

    Takes:
        User:
          - Only look at this users data
        Analyze data time:
          - Time to take average of
        Date range to predict:
          - must be in future
    """

    def __init__(
        self, user: User, analyze_range: TimeRange, prediction_range: TimeRange
    ) -> None:
        self.user = user
        self.analysis_range = analyze_range
        self.prediction_range = prediction_range
        all_transactions = Transaction.objects.filter(
            budget__user=user,
            date__range=toNativeTimeRange(analyze_range),
            prediction=False,
        )

        self.analyze_transactions = all_transactions.filter(income=False)
        self.income_transactions = all_transactions.filter(income=True)

        self.analysis_start, self.analysis_end = analyze_range
        self.days_in_analysis_period = daysBetween(self.analysis_range)

        self.prediction_start, self.prediction_end = prediction_range
        self.days_in_prediction_period = daysBetween(self.prediction_range)

        self.transactions_in_analysis_period = self.analyze_transactions.count()
        self.unique_budgets = self._get_unique_budgets()
        self.budget_odds_distribution = self._get_budget_odds_distribution()

        self.transaction_probability_distrobution = (
            self._get_transaction_probability_distrobution()
        )

    def run(self) -> "QuerySet[Transaction]":
        transactions: List[Transaction] = [
            *self._generate_transactions(),
            *self._generate_income_transactions(),
        ]

        ids = [trans.id for trans in transactions]
        return Transaction.objects.filter(id__in=ids)

    def _generate_transactions(self) -> List[Transaction]:
        transactions: List[Transaction] = []
        for day_delta in range(self.days_in_prediction_period):
            num_transactions_to_create = self._get_transactions_to_create_per_day()
            for _ in range(num_transactions_to_create):
                for (
                    budget,
                    budget_prob,
                ) in self.transaction_probability_distrobution.items():
                    if not roll(budget_prob["prob"]):
                        continue
                    tag = self._get_weighted_tag(budget_prob["tags"])

                    predicted_transaction = Transaction.objects.create(
                        budget=budget,
                        description=PREDICTION_TRANSACTION_DESCRIPTION,
                        amount=budget_prob["tags"][tag]["average_amount"],
                        date=self.prediction_start.shift(days=day_delta).datetime,
                        prediction=True,
                    )

                    predicted_transaction.tags.set([tag])
                    transactions.append(predicted_transaction)

        return transactions

    def _generate_income_transactions(self) -> List[Transaction]:
        user_info = UserInfo.objects.get(user=self.user)
        root_budget = Budget.objects.get(user=self.user, name=ROOT_BUDGET_NAME)
        paycheque_tag, _ = Tag.objects.get_or_create(name=PAYCHEQUE_TAG_NAME, user=self.user)

        paycheque_amount = round(
            (user_info.expected_monthly_net_income / 31)
            * user_info.income_frequency_days
        )
        transactions = []

        for day_delta in range(
            0, self.days_in_prediction_period, user_info.income_frequency_days
        ):
            date = self.prediction_start.shift(days=day_delta)
            paycheque = Transaction.objects.create(
                prediction=True,
                income=True,
                transfer=False,
                budget=root_budget,
                amount=paycheque_amount,
                date=date.date(),
                description=PREDICTION_TRANSACTION_DESCRIPTION,
            )
            paycheque.tags.set([paycheque_tag])
            transactions.append(paycheque)

        for day_delta in range(
            0, self.days_in_prediction_period, user_info.income_frequency_days * 2
        ):
            date = self.prediction_start.shift(days=day_delta)
            income_trans = add_monthly_income(user=self.user, date=date, prediction=True)
            transactions = [*transactions, *income_trans]

        return transactions

    def _get_transactions_to_create_per_day(self) -> int:
        # There can be more than one transaction every day
        ratio = self.transactions_in_analysis_period / self.days_in_analysis_period
        extra = ratio % 1

        num_transactions_to_create = int(ratio // 1)
        if roll(extra):
            num_transactions_to_create += 1
        return num_transactions_to_create

    @staticmethod
    def _get_weighted_tag(tags: Dict[Tag, TagProbDistro]) -> Tag:
        data = {tag: tags[tag]["prob"] for tag in tags}
        weights = list(data.values())
        keys = list(data.keys())
        return random.choices(keys, weights=weights, k=1)[0]

    def _get_transaction_probability_distrobution(self) -> ProbabilityDistrobution:
        """
        All probabilities at any level will add to one.

        Example:
            food:
              probability: 0.35%
              tags:
                groceries:
                  probability: 0.35%
                  average_amount: -356
                resteraunt:
                  probability: 0.65%
                  average_amount: -56
        """
        probability_distrobution: ProbabilityDistrobution = {}
        budget_odds = self.budget_odds_distribution.items()

        for budget, odds_of_trans_for_budget in budget_odds:
            budget_prob_distro: BudgetProbDistro = {
                "prob": odds_of_trans_for_budget,
                "tags": {},
            }
            transactions = self.analyze_transactions.filter(budget=budget)

            tag_odds_distribution = self._get_tag_odds_distribution(transactions)
            for tag, odds_of_tag in tag_odds_distribution.items():
                transactions_with_tag = transactions.filter(tags=tag)

                tag_prob_distro: TagProbDistro = {
                    "prob": odds_of_tag,
                    "average_amount": self._get_average_amount(transactions_with_tag),
                }
                budget_prob_distro["tags"][tag] = tag_prob_distro

            probability_distrobution[budget] = budget_prob_distro
        return probability_distrobution

    def _get_average_amount(self, transactions: "QuerySet[Transaction]") -> int:
        return round(transactions.aggregate(avg=Avg("amount"))["avg"])

    def _get_odds_of_transaction_occurence(
        self, transactions: "QuerySet[Transaction]"
    ) -> float:
        return transactions.count() / self.days_in_analysis_period

    def _get_unique_budgets(self) -> "QuerySet[Budget]":
        return Budget.objects.filter(
            pk__in=self.analyze_transactions.values_list("budget", flat=True)
        )

    def _get_unique_tags(
        self, transactions: "QuerySet[Transaction]"
    ) -> "QuerySet[Tag]":
        return Tag.objects.filter(pk__in=transactions.values_list("tags", flat=True))

    def _get_tag_odds_distribution(
        self, transactions: "QuerySet[Transaction]"
    ) -> Dict[Tag, float]:
        tags = self._get_unique_tags(transactions)
        total_transactions = transactions.count()

        def odds_of_tag(tag: Tag) -> float:
            return transactions.filter(tags=tag).count() / total_transactions

        return {tag: odds_of_tag(tag) for tag in tags}

    def _get_budget_odds_distribution(self) -> Dict[Budget, float]:
        def odds_of_budget(budget: Budget) -> float:
            return (
                self.analyze_transactions.filter(budget=budget).count()
                / self.transactions_in_analysis_period
            )

        return {budget: odds_of_budget(budget) for budget in self.unique_budgets}
