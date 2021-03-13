from rest_framework.test import APITestCase

from budget.utils.test import generate_budget, generate_user, generate_transaction


class TestBudget(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = generate_user()
        cls.budget = generate_budget(user=cls.user, initial_balance=1)
        cls.other_budget = generate_budget(user=cls.user)

    def test_balance(self):
        """
        Account balance should not include transfers
        """
        # included
        generate_transaction(budget=self.budget, amount=1, transfer=False),

        # Not included
        generate_transaction(budget=self.budget, amount=1, transfer=True),
        generate_transaction(budget=self.other_budget, amount=1, transfer=True),
        generate_transaction(budget=self.other_budget, amount=1, transfer=False)

        # 1 initial balance + 1 non transfer transaction
        self.assertEqual(self.budget.balance(), 2)
