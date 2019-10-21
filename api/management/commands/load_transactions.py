from django.core.management.base import BaseCommand, CommandError
from api.models import Transaction
import os

"""
takes input csv with following attributes:


Sample can be found in docs/csv/transaction.csv
"""
# TODO: add example csv to docs


class Command(BaseCommand):
    help = '''
    ----------------
    load_transaction
    ----------------
    
    Usage: 'python3 manage.py load_transactions path/to/file.csv'
    
    Input:
       path to csv file
       
       CSV must contain following attributes: 
            amount, budget, date, description
            
    '''

    def fail(self, msg):
        print("\nError: ", msg)
        print(self.help)
        exit(-1)

    def add_arguments(self, parser):
        # path to the csv containing transactions. Must exist
        parser.add_argument('input_csv', nargs='+', type=str, )

    def handle(self, *args, **options):
        """
        Procedure:
            - validate
            -

        """
        # only checking first argument
        csv_path = options['input_csv'][0]

        if not os.path.exists(csv_path):
            self.fail(f"Path '{csv_path}' doesn't exist")


