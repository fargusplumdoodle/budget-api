from django.core.management.base import BaseCommand
from api.load_scripts import load_budgets

"""
Sample can be found in docs/csv/transaction.csv
"""


class Command(BaseCommand):
    help = """
    ----------------
    load_transaction
    ----------------
    
    Usage: 'python3 manage.py load_transactions path/to/file.csv'
    
    Input:
       path to csv file
       
       CSV must contain following attributes: 
            amount, budget, date, description
            
        Sample can be found in docs/csv/transaction.csv
    """

    def add_arguments(self, parser):
        # path to the csv containing transactions. Must exist
        parser.add_argument("input_csv", nargs="+", type=str)

    def handle(self, *args, **options):
        # only checking first argument
        csv_path = options["input_csv"][0]

        load_budgets(csv_path)
