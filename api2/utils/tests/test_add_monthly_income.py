import arrow

from api2.constants import ROOT_BUDGET_NAME, INCOME_TAG_NAME
from api2.models import Budget, Tag, Transaction
from budget.utils.test import BudgetTestCase
from api2.utils.add_monthly_income import add_monthly_income


class AddIncomeTestCase(BudgetTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def test_no_root_budget(self):
        user = self.generate_user()
        add_monthly_income(user)

        self.assertTrue(
            Budget.objects.filter(user=user, name=ROOT_BUDGET_NAME).exists()
        )
        self.assertEqual(Transaction.objects.filter(budget__user=user).count(), 0)

    def test_no_income_tag(self):
        user = self.generate_user()
        add_monthly_income(user)

        self.assertTrue(Tag.objects.filter(user=user, name=INCOME_TAG_NAME).exists())
        self.assertEqual(Transaction.objects.filter(budget__user=user).count(), 0)

    def test_custom_date(self):
        user = self.generate_user()
        root = self.generate_budget(name=ROOT_BUDGET_NAME, user=user)
        child = self.generate_budget(parent=root, user=user, monthly_allocation=20)
        date = arrow.get(2020, 1, 1)

        add_monthly_income(user, date=date)

        self.assertTrue(
            Transaction.objects.filter(
                budget=child,
                amount=20,
                date=date.date(),
                description="Monthly Income",
                income=True,
                transfer=False,
                prediction=False,
                tags__name=INCOME_TAG_NAME,
            ).exists()
        )
        self.assertTrue(
            Transaction.objects.filter(
                budget=root,
                amount=-20,
                date=date.date(),
                description=f"Monthly Income: ${child.name}",
                income=True,
                transfer=False,
                prediction=False,
                tags__name=INCOME_TAG_NAME,
            ).exists()
        )

    def test_no_income_for_budgets_that_have_no_allocation_or_negative_allocation(self):
        user = self.generate_user()
        root = self.generate_budget(name=ROOT_BUDGET_NAME, user=user)
        self.generate_budget(parent=root, user=user, monthly_allocation=-20)
        self.generate_budget(parent=root, user=user, monthly_allocation=0)

        add_monthly_income(user)

        self.assertEqual(Transaction.objects.filter(budget__user=user).count(), 0)
