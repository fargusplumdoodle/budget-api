import arrow

from api2.constants import ROOT_BUDGET_NAME
from budget.utils.migrations import CustomMigration


class SetupCreatedAndModifiedTime(CustomMigration):
    def forward(self):
        Transaction = self.get_model("api2", "Transaction")

        for transaction in Transaction.objects.using(self.db).all():
            date = arrow.get(transaction.date)
            transaction.created = date.datetime
            transaction.modified = date.datetime
            transaction.save()

    def reverse(self):
        pass
