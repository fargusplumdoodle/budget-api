from api2.queries import get_all_children
from budget.utils.test import BudgetTestCase


class GetAllChildren(BudgetTestCase):
    def test(self):
        a, expected_children = self.generate_budget_tree()
        all_children = get_all_children(a)
        self.assertEqual({*all_children}, expected_children)
