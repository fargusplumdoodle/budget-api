from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from api2.models import Budget
from budget.settings import DEBUG
from api2.printer import Printer
from .generate_transactions import Command as GenerateTransactionsCommand


class Command(BaseCommand):
    help = """
    Creates 4 sample budgets with the dev user
    Generates transactions for those budgets
    """

    def add_arguments(self, parser):
        # path to the csv containing transactions. Must exist
        parser.add_argument(
            "--save", action="store_true", help="actually save to database"
        )

    def handle(self, *args, **options):
        if not DEBUG:
            raise EnvironmentError(
                "Will not generate transactions when DEBUG isnt True"
            )
        user, created = User.objects.get_or_create(username="dev")
        user.set_password("dev")
        user.save()

        budgets = [("food", 25), ("housing", 25), ("medical", 25), ("personal", 25)]
        for budget in budgets:
            Budget.objects.get_or_create(
                name=budget[0], percentage=budget[1], user=user
            )

        trans = GenerateTransactionsCommand.generate_transactions(
            timezone.now(), 10 * 2, 1980, save=options["save"]
        )
        Printer.print_transactions(trans)

        if not options["save"]:
            print()
            print(
                "WARNING: --save flag not set, no transactions were saved to the database"
            )
