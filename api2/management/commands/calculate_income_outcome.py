from django.core.management.base import BaseCommand

from api2.models import Budget


class Command(BaseCommand):
    help = """
    ----------------
    Calculate Budget Income and Outcome
    ----------------

    Goes through the last 3 months of transactions for each budget and determines the average income/outcome for
    that budget
    """

    def handle(self, *args, **options):
        for budget in Budget.objects.all():
            budget.calculate_income_outcome(save=True)
            self.stdout.write(
                self.style.SUCCESS(
                    'Budget "%s"\n'
                    "  - income: %s\n"
                    "  - outcome: %s\n"
                    % (budget.name, budget.income_per_month, budget.outcome_per_month)
                )
            )
