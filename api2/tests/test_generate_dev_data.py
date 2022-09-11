from django.contrib.auth.models import User

from api2.management.commands.generate_dev_data import Command as GenDevDataCommand
from api2.models import Budget, Transaction
from budget.utils.test import BudgetTestCase


class TestGenerateDevData(BudgetTestCase):
    def test(self):
        with self.settings(DEBUG=True):
            GenDevDataCommand().handle()

        # +1 for root budget that is auto generated
        number_of_root_budgets = User.objects.count()
        self.assertEqual(
            Budget.objects.count(),
            len(GenDevDataCommand.BUDGETS) + number_of_root_budgets,
        )
        for budget in Budget.objects.all():
            self.assertEqual(
                Transaction.objects.filter(budget=budget, prediction=False).count(),
                GenDevDataCommand.EXPECTED_TRANSACTIONS,
            )
