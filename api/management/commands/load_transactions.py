from django.core.management.base import BaseCommand, CommandError
from api.models import Transaction, Budget
import os
import csv

"""
Sample can be found in docs/csv/transaction.csv
"""


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
            
        Sample can be found in docs/csv/transaction.csv
    '''

    # To add new fields, add here and in csv loop
    REQUIRED_FIELDS = ['amount', 'budget', 'date', 'description']

    def fail(self, msg):
        print("\nError: ", msg)
        print(self.help)
        exit(-1)

    def add_arguments(self, parser):
        # path to the csv containing transactions. Must exist
        parser.add_argument('input_csv', nargs='+', type=str, )

    def invalid_csv_headers(self, csv_headers):
        """
        Checks if csv has appropriate headers

        :param csv_headers: a list of headers, example: ['amount', 'budget', 'date', 'description']
        :return: returns error message if true, returns null if false
        """
        for field in self.REQUIRED_FIELDS:
            if field not in csv_headers:
                return f'Missing field: "{field}" from csv'
        return None

    def handle(self, *args, **options):
        """
        Procedure:
            - validate
            -

        """
        # only checking first argument
        csv_path = options['input_csv'][0]

        # ensuring path exists
        if not os.path.exists(csv_path):
            self.fail(f"Path '{csv_path}' doesn't exist")

        # reading csv
        with open(csv_path, 'r') as csv_fl:

            # loading csv
            reader = csv.reader(csv_fl)

            # creating list of lists
            csv_data = [x for x in reader]
            headers = csv_data[0]

            # validation
            error = self.invalid_csv_headers(headers)
            if error is not None:
                self.fail(error)

            # getting
            for row in range(1, len(csv_data)):

                # creating budget if it doesn't exist
                budget, _ = Budget.objects.get_or_create(
                    name=csv_data[row][headers.index('budget')]
                )

                # MODIFY HERE WHEN NEW ATTRIBUTES ARE ADDED TO TRANSACTION
                try:
                    Transaction.objects.create(
                        amount=csv_data[row][headers.index('amount')],
                        description=csv_data[row][headers.index('description')],
                        budget=budget,
                        date=csv_data[row][headers.index('date')]
                    )
                except ValueError as e:
                    self.fail(f"Invalid Data: {e}")

