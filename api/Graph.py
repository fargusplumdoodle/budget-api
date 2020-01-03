from .models import Budget, Transaction
from django.db.models.query import QuerySet
from datetime import date
from datetime import timedelta
import random


class Graph:
    @staticmethod
    def get_days_to_process(days):
        """
        :param days: int, number of days 
        :returns: list of day numbers

        This function is for helping us find the number of plots
        on the graph history page.

            We have to have 14 or less plots
            --------------------------------

            So if there is less than or equal to 14 plots, we will show them

            otherwise, we have to remove random plots until the number is divisible
            by 14

            then when getting the days we are going to calculate we skip every day
            that isn't divisible by 14
        """
        if days <= 0:
            return []

        # if there are less than 14 days we show them all
        if days <= 14:
            return [x for x in range(days)]

        return [0] + [x for x in range(1, days - 1, int(days / 14))] + [days]

    @staticmethod
    def balance_history(budgets, start, end, show=False):
        """
        Generates a graph of the provided budgets over two dates

        :param budgets: queryset of budget objects
        :param start: start date
        :param end: end date
        :param show: if we show the plot after generation, dont use this
                        in prod
        :return: Python Dictionary
            {
                'days':['2019-10-11 00:21:30.307150', ...],
                'budgets': {
                        'budget_name': [125, 167, 35, ...],
                        ...
                }
            }

            days: a list of dates for each data point in each budget
            budgets: a dict of budgets and their datapoints for each day

            The datapoints are the balance of the budget at that particular time.
            More info in 'docs/api.md'
        """
        # validation
        assert isinstance(budgets, QuerySet)  # must be a query set of budgets
        assert len(budgets) != 0  # must be at lease one budget
        assert isinstance(start, date)  # must be datetime.date
        assert isinstance(end, date)  # must be datetime.date

        # generating time axis
        days = (end - start).days
        all_transactions = Transaction.objects.all()
        days_x = []

        # each key is a budget
        # each value is a list of the balance for each day
        budgets_y = {}
        for budget in budgets:
            budgets_y[budget] = []

        """
        This holds a key for each day
        """
        days_transactions = {}

        for x in Graph.get_days_to_process(days):
            # -------------------------------------
            # This gets a query of all transactions
            #   up to this day on all budgets
            # then associates it with a day
            # -------------------------------------
            current_day = start + timedelta(days=x)

            # finding all transactions up to this day
            transactions_up_to_today = all_transactions.filter(date__lt=current_day)

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

        # generating output data
        graph_data = {"days": [str(x) for x in days_x], "budgets": []}
        for budget_model in budgets_y:
            graph_data["budgets"].append(
                {"name": str(budget_model.name), "data": budgets_y[budget_model]}
            )

        return graph_data


