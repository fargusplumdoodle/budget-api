from django.core.management.base import BaseCommand, CommandError
from api.models import Budget
from api.helper import budgets_sum_to_one
import os
import csv

"""
Sample can be found in docs/csv/transaction.csv
"""


class Command(BaseCommand):
    OUTPUT_COL_WIDTH = 30
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
    REQUIRED_FIELDS = ['name', 'percentage', 'initial_balance']

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

        :param csv_headers: a list of headers, example: ['name', 'percentage', 'initial_balance']
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

            self.stdout.write("LOADED CSV")

            # generating header
            header = ("Budget".rjust(self.OUTPUT_COL_WIDTH) +
                                "Percentage".rjust(self.OUTPUT_COL_WIDTH) +
                              "Initial Balance".rjust(self.OUTPUT_COL_WIDTH))

            self.stdout.write( header + "\n" + str("-" * len(header)) + "\n")

            # setting values
            for row in range(1, len(csv_data)):

                # creating budget if it doesn't exist
                budget, _ = Budget.objects.get_or_create(
                    name=csv_data[row][headers.index('name')]
                )

                # MODIFY HERE WHEN NEW ATTRIBUTES ARE ADDED TO TRANSACTION
                try:
                    budget.percentage = csv_data[row][headers.index('percentage')]
                    budget.initial_balance = csv_data[row][headers.index('initial_balance')]
                    budget.save()

                    # Outputing information about budgets to user
                    budget_console_output = (f"{budget.name}".rjust(self.OUTPUT_COL_WIDTH) +
                              f"{budget.percentage}".rjust(self.OUTPUT_COL_WIDTH) +
                              f"{budget.initial_balance}".rjust(self.OUTPUT_COL_WIDTH))
                    self.stdout.write(budget_console_output + "\n")
                    self.stdout.write('*' * len(header))

                except ValueError as e:
                    self.fail(f"Invalid Data: {e}")

            # verifying budget was created correctly
            # this will be None if the budget is balanced
            budget_total = budgets_sum_to_one()
            if budget_total:
                self.stderr.write(f"WARNING: Budget not balanced! "
                                  f"Total percentages add to {budget_total}, they should add to 1"
                                  f"\nYou may want to revise your budgets")
