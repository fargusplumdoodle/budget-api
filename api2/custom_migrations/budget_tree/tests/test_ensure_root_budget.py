from unittest import skip

from api2.constants import ROOT_BUDGET_NAME
from api2.custom_migrations.budget_tree.EnsureRootBudget import EnsureRootBudget
from api2.models import Budget
from budget.utils.test import BudgetTestCase


@skip("Migrations dont need to be tested")
class EnsureRootBudgetTestCase(BudgetTestCase):
    @staticmethod
    def forward():
        migration = EnsureRootBudget(app=None, db="default", testing=True)
        migration.forward()

    def test_ensure_root_budgets_are_created_for_each_user(self):
        orphan_budgets = [self.generate_budget(parent=None) for _ in range(3)]

        self.forward()

        root_budget = Budget.objects.get(user=self.user, name=ROOT_BUDGET_NAME)
        for budget in orphan_budgets:
            budget.refresh_from_db()

            self.assertEqual(budget.parent, root_budget)

        self.assertIsNone(root_budget.parent)
