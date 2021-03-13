import arrow
from rest_framework.reverse import reverse

from api2.models import Transaction
from budget.utils.test import BudgetTestCase


class IncomeTestCase(BudgetTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.budgets_with_percentage = [
            cls.generate_budget(percentage=25),
            cls.generate_budget(percentage=25),
            cls.generate_budget(percentage=25),
            cls.generate_budget(percentage=25),
        ]
        cls.budget_without_percentage = (cls.generate_budget(percentage=0),)

    def test_add_income(self):
        data = {
            'amount': 100_00,
            'description': "income example",
            'date': arrow.now().date(),
        }
        r = self.post(reverse('api2:transaction-income'), data=data)
        response = r.json()

        transactions = Transaction.objects.all()
        self.assertEqual(transactions.count(), 4)

        for trans_json in response:
            trans = Transaction.objects.get(id=trans_json['id'])
            self.assertEqual(trans.amount, data['amount'] / 4)
            self.assertIn(trans.budget, self.budgets_with_percentage)
            self.assertEqual(arrow.get(trans.date).date(), data['date'])
            self.assertEqual(trans.description, data['description'])
            self.assertEqual(trans.income, True)
            self.assertEqual(trans.transfer, False)

