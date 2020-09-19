from django.contrib.auth.models import User

from api2.utils import add_income

from django.core.management.base import BaseCommand
from api.helper import generate_transactions
from django.utils import timezone
from budget.settings import DEBUG
from api2.printer import Printer

"""
Sample can be found in docs/csv/transaction.csv """


class Command(BaseCommand):
    help = """
    ----------------
    generate transactions
    ----------------

    Usage: 'python3 manage.py generate_transactions'

    Refuses to run when DEBUG is True

    Generates the last n paycheques, assuming you got payed every 2 weeks.
    creates for each user

    parameters
        $1: int number of paycheques
        $2: float amount per paycheque

    IDEAS:
        maybe a random transaction generator class
        - varying number of  transactions ( x < 100 )
        - varying amounts (-10 < x < 10)
        - varying duration between (1 < x < 10) days apart
        - evenly distrobuted across budgets

    """

    def add_arguments(self, parser):
        # path to the csv containing transactions. Must exist
        parser.add_argument("months", nargs="+", type=int)
        parser.add_argument("amount", nargs="+", type=int)
        parser.add_argument(
            "--save", action="store_true", help="actually save to database"
        )

    def handle(self, *args, **options):
        if not DEBUG:
            raise EnvironmentError(
                "Will not generate transactions when DEBUG isnt True"
            )

        # only checking first argument
        months = int(options["months"][0])
        amount = int(options["amount"][0])

        trans = generate_transactions(
            timezone.now(), months * 2, amount, save=options["save"]
        )

        Printer.print_transactions(trans)

        if not options["save"]:
            print()
            print(
                "WARNING: --save flag not set, no transactions were saved to the database"
            )

    @staticmethod
    def generate_transactions(start_date, num_paycheques, income, save=False):
        """
        Creates a bunch of transactions. This function is largly for testing

        Calls add_money to generate transactions, this will add num_paycheques * x where x is
        the number of budgets that exist.

        REPEATS OPERATION FOR THE FIRST 5 USERS IT FINDS

        :param start_date: start date, datetime
        :param num_paycheques: number of paycheques to generate
        :param income: amount you make per 14 days
        :param save: if true we will save transactions, doesn't work in debug
        :return: list of transacitons
        """
        if not DEBUG and save:
            raise EnvironmentError("Will not generate transactions when DEBUG is True")

        number_of_days_between_paychecks = 14

        # wont save unless we are in debug mode
        save = save and DEBUG

        transactions = []
        for user in User.objects.all()[:5]:
            for x in range(-num_paycheques, 0):
                date = start_date - timezone.timedelta(days=-int(number_of_days_between_paychecks * x))
                transactions = transactions + add_income(amount=int(income), user=user, date=date, save=save)

        # returning transacions
        return transactions
