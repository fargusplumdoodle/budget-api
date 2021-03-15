from budget.utils.test import BudgetTestCase
from api2.utils import budgets_sum_to_one


class UtilsTestCase(BudgetTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def test_budgets_sum_to_one(self):
        user2 = self.generate_user()

        self.generate_budget(user=user2, percentage=80),
        self.generate_budget(user=user2, percentage=10),
        self.assertFalse(budgets_sum_to_one(user=user2))

        self.generate_budget(user=self.user, percentage=25),
        self.generate_budget(user=self.user, percentage=25),
        self.generate_budget(user=self.user, percentage=25),
        self.generate_budget(user=self.user, percentage=25),
        self.assertTrue(budgets_sum_to_one(user=self.user))
