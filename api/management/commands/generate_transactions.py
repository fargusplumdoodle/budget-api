from django.core.management.base import BaseCommand, CommandError
from api.helper import generate_transactions
from django.utils import timezone
from budget.settings import DEBUG

"""
Sample can be found in docs/csv/transaction.csv """


class Command(BaseCommand):
    help = """
    ----------------
    generate transactions
    ----------------
    
    Usage: 'python3 manage.py generate_transactions'
    
    Refuses to run when DEBUG is True
    
    Generates the last n paycheques, assuming you got payed every 2 weeks
    
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

    def handle(self, *args, **options):
        if not DEBUG:
            raise EnvironmentError("Will not generate transactions when DEBUG is True")

        # only checking first argument
        months = int(options["months"][0])
        amount = int(options["amount"][0])

        generate_transactions(timezone.now(), months * 2, amount)
