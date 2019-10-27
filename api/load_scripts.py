from api.models import Transaction, Budget
import os
import csv


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
            budget, _ = Budget.objects.get_or_create(
                name=csv_data[row][headers.index("budget")]
            )

            # MODIFY HERE WHEN NEW ATTRIBUTES ARE ADDED TO TRANSACTION
            try:
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
    print("\nError: ", msg)
    print(self.help)
    exit(-1)
