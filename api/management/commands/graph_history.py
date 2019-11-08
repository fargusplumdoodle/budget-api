from django.core.management.base import BaseCommand, CommandError
from api.Graph import Graph
from django.utils import timezone
from budget.settings import DEBUG
from api.models import Budget
from datetime import date

"""
Sample can be found in docs/csv/transaction.csv """


class Command(BaseCommand):
    help = """
    ----------------
    Graph History
    ----------------

    Usage: 'python3 manage.py graph_history'

    Generates a graph for the 
    """

    def add_arguments(self, parser):
        # path to the csv containing transactions. Must exist
        # parser.add_argument("months", nargs="+", type=int)
        pass

    def handle(self, *args, **options):
        if not DEBUG:
            raise EnvironmentError("Will not generate transactions when DEBUG is True")

        # only checking first argument
        # months = int(options["months"][0])
        # amount = int(options["amount"][0])

        budgets = Budget.objects.all()
        start = date(2019, 10, 15)
        end = date(2019, 12, 5)
        Graph.balance_history(budgets, start, end)
