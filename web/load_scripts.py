from web.models import Transaction, Budget
from .helper import budgets_sum_to_one

from django.core.management.base import CommandError
import os
import csv


def load_budgets(csv_path, verbose=True):
    # To add new fields, add here and in csv loop
    output_col_width = 20
    required_fields = ["name", "percentage", "initial_balance"]

    # ensuring path exists
    if not os.path.exists(csv_path):
        fail(f"Path '{csv_path}' doesn't exist")

    # reading csv
    with open(csv_path, "r") as csv_fl:

        # loading csv
        reader = csv.reader(csv_fl)

        # creating list of lists
        csv_data = [x for x in reader]
        headers = csv_data[0]

        # validation
        error = invalid_csv_headers(required_fields, headers)
        if error is not None:
            fail(error)

        if verbose:
            print("LOADED CSV")

            # generating header
            header = (
                "Budget".rjust(output_col_width)
                + "Percentage".rjust(output_col_width)
                + "Initial Balance".rjust(output_col_width)
            )

            print(header + "\n" + str("-" * len(header)) + "\n")

        # setting values
        for row in range(1, len(csv_data)):

            # MODIFY HERE WHEN NEW ATTRIBUTES ARE ADDED TO TRANSACTION
            try:
                # creating budget if it doesn't exist
                budget, _ = Budget.objects.get_or_create(
                    name=csv_data[row][headers.index("name")],
                    percentage=csv_data[row][headers.index("percentage")],
                    initial_balance=csv_data[row][headers.index("initial_balance")],
                )
                budget.save()

                if verbose:
                    # Outputing information about budgets to user
                    budget_console_output = (
                        f"{budget.name}".rjust(output_col_width)
                        + f"{budget.percentage}".rjust(output_col_width)
                        + f"{budget.initial_balance}".rjust(output_col_width)
                    )
                    print(budget_console_output + "\n")

            except ValueError as e:
                fail(f"Invalid Data: {e}")

        # verifying budget was created correctly
        # this will be None if the budget is balanced
        budget_total = budgets_sum_to_one()
        if budget_total:
            print(
                f"WARNING: Budget not balanced! "
                f"Total percentages add to {budget_total}, they should add to 1"
                f"\nYou may want to revise your budgets"
            )


def load_transactions(csv_path):
    # To add new fields, add here and in csv loop
    required_fields = ["amount", "budget", "date", "description"]

    # ensuring path exists
    if not os.path.exists(csv_path):
        fail(f"Path '{csv_path}' doesn't exist")

    # reading csv
    with open(csv_path, "r") as csv_fl:
        # loading csv
        reader = csv.reader(csv_fl)

        # creating list of lists
        csv_data = [x for x in reader]
        headers = csv_data[0]

        # validation
        error = invalid_csv_headers(required_fields, headers)
        if error is not None:
            fail(error)

        # getting
        for row in range(1, len(csv_data)):

            # creating budget if it doesn't exist
            if (
                len(Budget.objects.filter(name=csv_data[row][headers.index("budget")]))
                != 1
            ):
                fail(f'Budget "{csv_data[row][headers.index("budget")]}" doesnt exist')

            # MODIFY HERE WHEN NEW ATTRIBUTES ARE ADDED TO TRANSACTION
            try:
                budget = Budget.objects.get(name=csv_data[row][headers.index("budget")])
                Transaction.objects.create(
                    amount=csv_data[row][headers.index("amount")],
                    description=csv_data[row][headers.index("description")],
                    budget=budget,
                    date=csv_data[row][headers.index("date")],
                )
            except ValueError as e:
                fail(f"Invalid Data: {e}")


def invalid_csv_headers(required_headers, csv_headers):
    """
    Checks if csv has appropriate headers

    :param required_headers: a list of headers that are required to exist, example: ['amount', 'budget', 'date', 'description']
    :param csv_headers: a list of headers from the csv file, example: ['amount', 'budget', 'date', 'description']
    :return: returns error message if true, returns null if false
    """
    for field in required_headers:
        if field not in csv_headers:
            return f'Missing field: "{field}" from csv'
    return None


def fail(msg):
    raise CommandError("\nError: " + msg)
