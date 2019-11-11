from django.core.management.base import BaseCommand, CommandError
from api.Graph import Graph
from api.models import Budget
from datetime import datetime
from datetime import timedelta

"""
Sample can be found in docs/csv/transaction.csv """


class Command(BaseCommand):
    help = """
    ----------------
    Graph History
    ----------------

    Usage: 'python3 manage.py graph_history'

    Generates a graph for the last x month of transactions
    
    Parameters:
        1: number of previous months to graph
    """

    def add_arguments(self, parser):
        # path to the csv containing transactions. Must exist
        parser.add_argument("months", nargs="+", type=int)
        pass

    def handle(self, *args, **options):
        # only checking first argument
        months = int(options["months"][0])

        budgets = Budget.objects.all()
        start = datetime.now() - timedelta(days=31 * months)
        end = datetime.now()
        Graph.balance_history(budgets, start, end)
