from django.core.management.base import BaseCommand
from web.load_scripts import load_budgets
from web.models import Transaction
from web.printer import Printer

"""
Sample can be found in docs/csv/transaction.csv
"""


class Command(BaseCommand):
    help = """
    ----------------
    print_transactions 
    ----------------
    
    Will print the x most recent transactions
    
    Input:
        number of transactions to show
       
    """

    def add_arguments(self, parser):
        # path to the csv containing transactions. Must exist
        parser.add_argument("num_transactions", nargs="+", type=int)

    def handle(self, *args, **options):
        # only checking first argument
        num_transactions = options["num_transactions"][0]

        trans = list(Transaction.objects.order_by('date'))
        Printer.print_transactions(
            list(trans[0 - num_transactions:])
        )
