from api2.models import Budget
from cron.cron import CronJob


class CalculateIncomeOutcome(CronJob):
    """
    ----------------
    Calculate Budget Income and Outcome
    ----------------

    Goes through the last 3 months of transactions for each budget and determines the average income/outcome for
    that budget
    """

    name = "Calculate Budget Income Outcome"

    def run(self, *args, **options):
        for budget in Budget.objects.all():
            budget.calculate_income_outcome(save=True, time_period=3)
