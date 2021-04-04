import arrow
from django.contrib.auth.models import User
from django.core.serializers.base import Serializer
from django.db.models import Model
from rest_framework.reverse import reverse

from api2.models import Transaction, Budget, Tag
from api2.serializers import BudgetSerializer, TagSerializer
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
            "amount": 100_00,
            "description": "income example",
            "date": arrow.now().date(),
        }
        r = self.post(reverse("api2:transaction-income"), data=data)
        response = r.json()

        transactions = Transaction.objects.all()
        self.assertEqual(transactions.count(), 4)

        for trans_json in response:
            trans = Transaction.objects.get(id=trans_json["id"])
            self.assertEqual(trans.amount, data["amount"] / 4)
            self.assertIn(trans.budget, self.budgets_with_percentage)
            self.assertEqual(arrow.get(trans.date).date(), data["date"])
            self.assertEqual(trans.description, data["description"])
            self.assertEqual(trans.income, True)
            self.assertEqual(trans.transfer, False)


class UserRelatedModelViewSetMixin:
    model: Model
    serializer: Serializer

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user1 = cls.generate_user()

        reverse_url = "api2:" + cls.model.__name__.lower()
        cls.detail_url = reverse_url + "-detail"
        cls.list_url = reverse_url + "-list"

    def setUp(self) -> None:
        self.user_objs = []
        for _ in range(10):
            self.user_objs.append(self.generate_obj(self.user))

        self.user1_objs = []
        for _ in range(10):
            self.user1_objs.append(self.generate_obj(self.user1))

    @classmethod
    def generate_obj(cls, user: User):
        generator = getattr(cls, f"generate_{cls.model.__name__.lower()}")
        return generator(user=user)

    def test_get_list(self):
        r = self.get(reverse(self.list_url), user=self.user).json()
        self.assertEqual(len(r), len(self.user_objs))

        for obj in r:
            self.assertTrue(
                self.model.objects.filter(id=obj["id"], user=self.user.id).exists()
            )

    def test_get_detail(self):
        obj = self.user_objs[0]
        r = self.get(reverse(self.detail_url, (obj.id,)), user=self.user).json()
        self.assertEqual(r["id"], obj.id)
        if hasattr(obj, "name"):
            self.assertEqual(r["name"], obj.name)

    def test_create(self):
        obj = self.user_objs[0]
        data = self.serializer(obj).data
        obj.delete()

        del data["id"]
        # Not all serializers will have the user visible
        if "user" in data:
            del data["user"]

        r = self.post(reverse(self.list_url), data, user=self.user).json()
        self.assertTrue(self.model.objects.filter(id=r["id"], user=self.user).exists())


class BudgetViewSetTestCase(UserRelatedModelViewSetMixin, BudgetTestCase):
    serializer = BudgetSerializer
    model = Budget


class TagViewSetTestCase(UserRelatedModelViewSetMixin, BudgetTestCase):
    serializer = TagSerializer
    model = Tag
