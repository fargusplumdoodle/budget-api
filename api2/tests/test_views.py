import arrow
from django.contrib.auth.models import User
from django.core.serializers.base import Serializer
from django.db.models import Model, Q
from rest_framework.reverse import reverse

from api2.models import Transaction, Budget, Tag
from api2.serializers import BudgetSerializer, TagSerializer
from budget.utils.test import BudgetTestCase

now = arrow.get(2021, 1, 1)


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
            self.assertEqual(trans.tags.count(), 1)
            self.assertEqual(trans.tags.first().name, "income")


class ReportTestCase(BudgetTestCase):
    url = reverse("api2:report-list")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.budget = cls.generate_budget()
        cls.budget2 = cls.generate_budget()

        cls.start = now.shift(weeks=-1)
        cls.end = now

        # out of range
        cls.generate_transaction(
            cls.budget, amount=-100, date=cls.start.shift(weeks=-1).datetime
        )

        cls.in_range = []
        for x in range(7):
            cls.in_range.append(
                cls.generate_transaction(
                    cls.budget, date=cls.start.shift(days=x).datetime, amount=-100
                )
            )
        cls.in_range.append(
            cls.generate_transaction(
                cls.budget, amount=100, date=cls.start.shift(days=1), income=True
            )
        )

    def test_missing_required_parameters(self):
        r = self.get(self.url)
        self.assertEqual(r.status_code, 200, r.json())
        self.assertEqual(r.json()["budgets"], {})

    def test_budget_stats(self):
        r = self.get(
            self.url,
            query={"date__gte": self.start.date(), "date__lte": self.end.date()},
        )
        self.assertEqual(r.status_code, 200, r.json())
        data = r.json()

        self.assertEqual(len(data["transactions"]), len(self.in_range))
        self.assertEqual(len(data["budgets"]), 1)
        budget_stats = data["budgets"][str(self.budget.id)]
        self.assertEqual(
            budget_stats["initial_balance"],
            self.budget.balance(Q(date__lt=self.start.date())),
        )
        self.assertEqual(
            budget_stats["final_balance"],
            self.budget.balance(Q(date__lte=self.end.date())),
        )
        self.assertEqual(budget_stats["income"], 100)
        self.assertEqual(budget_stats["outcome"], -700)
        self.assertEqual(
            budget_stats["difference"],
            budget_stats["income"] - budget_stats["outcome"],
        )


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
        del data["user"]

        r = self.post(reverse(self.list_url), data, user=self.user)
        self.assertEqual(r.status_code, 201)
        self.assertTrue(
            self.model.objects.filter(id=r.json()["id"], user=self.user).exists()
        )

    def test_update(self):
        obj = self.user_objs[0]
        data = self.serializer(obj).data

        del data["id"]
        del data["user"]
        data["name"] = "certainly different"
        before_count = self.model.objects.count()

        r = self.put(reverse(self.detail_url, (obj.id,)), data, user=self.user)
        self.assertEqual(r.status_code, 200)
        response_data = r.json()
        self.assertTrue(
            self.model.objects.get(
                id=response_data["id"], name=data["name"], user=self.user
            )
        )
        self.assertEqual(before_count, self.model.objects.count())

    def test_create_different_user_specified(self):
        obj = self.user_objs[0]
        data = self.serializer(obj).data
        obj.delete()

        del data["id"]
        data["user"] = self.user1.id

        r = self.post(reverse(self.list_url), data, user=self.user).json()
        self.assertTrue(self.model.objects.filter(id=r["id"], user=self.user).exists())

    def test_create_unique_name_and_user(self):
        obj = self.user_objs[0]
        data = self.serializer(obj).data
        obj.delete()

        del data["id"]
        del data["user"]

        r = self.post(reverse(self.list_url), data, user=self.user)
        self.assertEqual(r.status_code, 201)
        self.assertTrue(
            self.model.objects.filter(id=r.json()["id"], user=self.user).exists()
        )

        r = self.post(reverse(self.list_url), data, user=self.user)
        self.assertEqual(r.status_code, 400)


class BudgetViewSetTestCase(UserRelatedModelViewSetMixin, BudgetTestCase):
    serializer = BudgetSerializer
    model = Budget


class TagViewSetTestCase(UserRelatedModelViewSetMixin, BudgetTestCase):
    serializer = TagSerializer
    model = Tag
