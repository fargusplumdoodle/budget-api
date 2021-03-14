from budget.utils.test import BudgetTestCase


class TestBudget(BudgetTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user = cls.generate_user()
        cls.budget = cls.generate_budget(user=cls.user, initial_balance=1)
        cls.other_budget = cls.generate_budget(user=cls.user)

    def test_balance(self):
        """
        Account balance should not include transfers
        """
        # included
        self.generate_transaction(budget=self.budget, amount=1, transfer=False),
        self.generate_transaction(budget=self.budget, amount=1, transfer=True),

        # Not included
        self.generate_transaction(budget=self.other_budget, amount=1, transfer=True),
        self.generate_transaction(budget=self.other_budget, amount=1, transfer=False)

        # 1 initial balance + 1 non transfer transaction
        self.assertEqual(self.budget.balance(), 3)
