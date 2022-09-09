from typing import Optional

import arrow
from django.db.models import QuerySet, Count

from api2.models import Tag, Transaction, Budget
from cron.cron import CronJob


class UpdateTagStats(CronJob):
    """
    Updates common tag stats including:
     - Frequency Ranking: How often this tag is used
     - Most common budget: Most frequent budget used with this tag
     - Most common amount: Most common amounts used with this tag
    """

    name = "Update Tag Stats"

    def run(self, *args, **kwargs):
        last_6_months = arrow.now().shift(months=-6).datetime

        for tag in Tag.objects.all():
            transactions = Transaction.objects.filter(
                tags=tag, date__gte=last_6_months, prediction=False
            ).prefetch_related("budgets")
            tag.rank = self.get_rank(transactions)
            tag.common_budget = self.get_common_budget(transactions)
            tag.common_transaction_amount = self.get_common_amount(transactions)
            tag.save()

    @staticmethod
    def get_rank(transactions: QuerySet[Transaction]) -> int:
        return transactions.count()

    @staticmethod
    def get_common_budget(transactions: QuerySet[Transaction]) -> Optional[Budget]:
        try:
            most_common_budget_pk = (
                transactions.values("budget")
                .annotate(count=Count("pk"))
                .order_by("-count")[0]["budget"]
            )
            return Budget.objects.get(pk=most_common_budget_pk)
        except IndexError:
            return None

    @staticmethod
    def get_common_amount(transactions: QuerySet[Transaction]) -> Optional[int]:
        try:
            return (
                transactions.values("amount")
                .annotate(count=Count("amount"))
                .order_by("-count")[0]["amount"]
            )
        except IndexError:
            return None
