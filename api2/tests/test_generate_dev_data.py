from api2.management.commands.generate_dev_data import Command as GenDevDataCommand
from api2.models import Budget, Transaction
from budget.utils.test import BudgetTestCase


class TestGenerateDevData(BudgetTestCase):
    def test(self):
        with self.settings(DEBUG=True):
            GenDevDataCommand().handle()

        self.assertEqual(Budget.objects.count(), len(GenDevDataCommand.BUDGETS))
        for budget in Budget.objects.all():
            self.assertEqual(
                Transaction.objects.filter(budget=budget).count(),
                GenDevDataCommand.EXPECTED_TRANSACTIONS,
            )
