import arrow

from api2.models import Transaction, Budget
from cron.cron import CronJob


class UpdateBudgetRankings(CronJob):
    name = "Update Budget Frequency Rankings"

    def run(self, *args, **kwargs):
        last_6_months = arrow.now().shift(months=-6).datetime

        for budget in Budget.objects.all():
            budget.rank = Transaction.objects.filter(
                budget=budget, date__gte=last_6_months
            ).count()
            budget.save()
