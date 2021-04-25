import random

from django.core.management.base import BaseCommand
from django.db import IntegrityError

from api2.models import Budget, Tag, Transaction
from budget.utils.test import BudgetTestCase


class Command(BaseCommand):
    help = """
    Generates sample budgets,transactions and tags
    """

    def add_arguments(self, parser):
        # path to the csv containing transactions. Must exist
        parser.add_argument(
            "--save", action="store_true", help="actually save to database"
        )

    def handle(self, *args, **options):
        try:
            u = BudgetTestCase.generate_user(username="dev")
            u.set_password("dev")
            u.save()
        except IntegrityError:
            self.stdout.write("dev user already exists, skipping generation")
            exit()

        Budget.objects.all().delete()
        Transaction.objects.all().delete()
        Tag.objects.all().delete()

        budgets = ["food", "transportation", "medical", "personal"]

        tag_names = [
            "groceries",
            "car",
            "doritos",
            "magic cards",
            "bike",
            "skip the dishes",
        ]
        for budget in budgets:
            BudgetTestCase.generate_budget(name=budget, user=u, percentage=25)

        for tag in tag_names:
            BudgetTestCase.generate_tag(name=tag, user=u)

        tags = Tag.objects.all()
        for budget in Budget.objects.all():
            for x in range(100):
                t = BudgetTestCase.generate_transaction(budget=budget)
                t.tags.add(random.choice(tags))
                t.tags.add(random.choice(tags))
                t.save()
