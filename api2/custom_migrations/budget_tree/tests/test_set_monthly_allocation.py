from unittest import skip

from api2.custom_migrations.budget_tree.SetMonthlyAllocation import SetMonthlyAllocation
from budget.utils.test import BudgetTestCase


@skip("Migrations dont need to be tested")
class SetMonthlyAllocationTestCase(BudgetTestCase):
    @staticmethod
    def forward():
        migration = SetMonthlyAllocation(app=None, db="default", testing=True)
        migration.forward()

    def test(self):
        budget = self.generate_budget(outcome_per_month=30)

        self.forward()

        budget.refresh_from_db()
        self.assertEqual(budget.monthly_allocation, budget.outcome_per_month)
