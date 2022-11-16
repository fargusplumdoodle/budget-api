from api2.queries import get_all_children
from budget.utils.test import BudgetTestCase


class GetAllChildren(BudgetTestCase):
    def test_with_children(self):
        root, nodes, children = self.generate_budget_tree()
        all_children = get_all_children(root)
        self.assertEqual({*all_children}, {*children, *nodes})

    def test_without_children(self):
        budget_with_no_children = self.generate_budget()
        all_children = get_all_children(budget_with_no_children)
        self.assertEqual([*all_children], [])
