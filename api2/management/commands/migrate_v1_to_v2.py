from django.contrib.auth.models import User

from django.core.management.base import BaseCommand, CommandError
from api.models import Budget as Budget1, Transaction as Transaction1
from api2.models import Budget as Budget2, Transaction as Transaction2


class Command(BaseCommand):
    help = """
    Converts all api-v1 Budgets,Transactions to api-v2 
    
    User supplied will inherit all existing budgets and transactions
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--save", action="store_true", help="actually save to database"
        )
        parser.add_argument(
            "user", nargs="+", type=str, help="Username to move existing budget to"
        )

    def handle(self, *args, **options):

        try:
            self.v1_to_v2(options["user"][1], options["save"])
        except IndexError:
            raise CommandError("Insufficient arguments supplied")

    @staticmethod
    def v1_to_v2(user, save):
        print("Searching for user: ", user)
        user = User.objects.get(username=user)

        print("BUDGETS")
        print("-------------------")
        print("Budget1, Budget2")
        for budget1 in Budget1.objects.all():
            budget2 = Budget2(
                name=budget1.name,
                percentage=round(budget1.percentage * 100),
                initial_balance=Command.convert_dollars_to_cents(
                    budget1.initial_balance
                ),
                user=user,
            )
            if save:
                budget2.save()

            print(budget1.name, budget2.name)
            print(budget1.percentage, budget2.percentage)
            print(budget1.initial_balance, budget2.initial_balance)
            print(budget2.user)
            print()
        print()
        print("TRANSACTIONS")
        print("-------------------")
        for transaction1 in Transaction1.objects.all():
            budget = (
                Budget2.objects.get(name=transaction1.budget.name)
                if save
                else Budget2(name=transaction1.budget.name)
            )
            transaction2 = Transaction2(
                amount=Command.convert_dollars_to_cents(transaction1.amount),
                description=transaction1.description,
                budget=budget,
                date=transaction1.date,
            )
            if save:
                transaction2.save()
            print(
                budget.name,
                transaction1.amount,
                transaction2.amount,
            )

    @staticmethod
    def convert_dollars_to_cents(amount):
        return round(amount * 100)

    @staticmethod
    def convert_cents_to_dollars(amount):
        return round(amount / 100, 2)
