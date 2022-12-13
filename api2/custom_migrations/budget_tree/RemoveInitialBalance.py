import arrow

from api2.models import Budget, Transaction
from budget.utils.migrations import CustomMigration

INITIAL_BALANCE_TRANSACTION_DESCRIPTION = "Initial balance transaction"
INITIAL_BALANCE_TAG_NAME = "Initial Balance"


class RemoveInitialBalance(CustomMigration):
    def get_date_of_first_transaction(self, Transaction: Transaction, budget: Budget):
        first_transaction = (
            Transaction.objects.using(self.db)
            .filter(budget__user=budget.user)
            .order_by("date")
            .first()
        )
        return first_transaction.date if first_transaction else arrow.now().datetime

    def forward(self):
        Budget = self.get_model("api2", "Budget")
        Transaction = self.get_model("api2", "Transaction")
        Tag = self.get_model("api2", "Tag")

        for budget in Budget.objects.using(self.db).exclude(initial_balance=0):
            first_day = self.get_date_of_first_transaction(Transaction, budget)

            tag, _ = Tag.objects.using(self.db).get_or_create(
                name=INITIAL_BALANCE_TAG_NAME, user=budget.user
            )

            trans = Transaction.objects.using(self.db).create(
                amount=budget.initial_balance,
                description=INITIAL_BALANCE_TRANSACTION_DESCRIPTION,
                budget=budget,
                date=first_day,
            )
            trans.tags.set([tag])

            budget.initial_balance = 0
            budget.save()

    def reverse(self):
        pass
