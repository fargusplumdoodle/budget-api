import matplotlib.pyplot as plt
from .models import Budget, Transaction
from django.db.models.query import QuerySet
from datetime import date
from datetime import timedelta


class Graph:
    @staticmethod
    def balance_history(budgets, start, end, show=False):
        """
        Generates a graph of the provided budgets over two dates
        :param budgets: queryset of budget objects
        :param start: start date
        :param end: end date
        :param show: if we show the plot after generation
        """
        # validation
        assert isinstance(budgets, QuerySet)  # must be a query set of budgets
        assert len(budgets) != 0  # must be at lease one budget
        assert isinstance(start, date)  # must be datetime.date
        assert isinstance(end, date)  # must be datetime.date

        # generating time axis
        days = (end - start).days

        days_x = []

        # each key is a budget
        # each value is a list of the balance for each day
        budgets_y = {}
        for budget in budgets:
            budgets_y[budget] = []

        # creating a dictionary of dates to list of all transactions up to that date
        days_transactions = {}
        for x in range(days):
            # finding current day
            current_day = start + timedelta(days=x)

            # finding all transactions up to this day
            transactions_up_to_today = Transaction.objects.filter(date__lt=current_day)

            # setting this date to those transactions
            days_transactions[current_day] = transactions_up_to_today

        # generating days by
        for day in days_transactions:
            # adding this  day to the X axis
            days_x.append(day)
            # print(type(day), days_transactions[day])
            for budget in budgets:
                # calculating balance of budget on this day. This adds up the amount of all transactions
                #  up until this day, then adds the inital_balance
                budgets_y[budget].append(
                    sum(x.amount for x in days_transactions[day].filter(budget=budget))
                    + budget.initial_balance
                )

        for budget in budgets:
            plt.plot(days_x, budgets_y[budget], label=budget.name)
        plt.legend()
        plt.show()