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

    def add_arguments(self, parser):
        # path to the csv containing transactions. Must exist
        parser.add_argument(
            "--save", action="save_true", help="Save changes to database"
        )

    def handle(self, *args, **options):
        self.calculate_income_outcome(save=options["save"])

    @staticmethod
    def calculate_income_outcome(save=False):
        for budget in Budget.objects.all():
            budget.calculate_income_outcome(save=save)
