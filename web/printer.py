from api.models import Transaction


class Printer:
    @staticmethod
    def print_transactions(transaction_list, col_width=15):
        """
        Takes a list of transactions and prints them nicely
        :param transaction_list: list of transaction objects to print the amount, budget, and date
                                  values of
        """
        # validation
        assert isinstance(transaction_list, list)
        for x in transaction_list:
            assert isinstance(x, Transaction)

        # generating header
        header = "amount".ljust(col_width) + 'budget'.ljust(col_width) + "date".ljust(col_width)
        divider = len(header) * '-'

        # printing  header
        print()
        print()
        print("TRANSACTIONS".rjust(int(len(divider) / 2)).ljust(int(len(divider) / 2)))
        print(divider)
        print(header)
        print(divider)

        # printing transactions
        for trans in transaction_list:
            print(
                str("%.2f" % float(trans.amount)).ljust(col_width) +
                str(trans.budget).ljust(col_width),
                str(trans.date).ljust(col_width),
            )
