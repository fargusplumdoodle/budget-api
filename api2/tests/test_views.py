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

    def setUp(self):
        super().setUpTestData()
        self.budget = self.generate_budget()
        self.budget2 = self.generate_budget()

        self.start = now.shift(weeks=-1)
        self.end = now

        # out of range
        self.generate_transaction(
            self.budget, amount=-100, date=self.start.shift(weeks=-1).datetime
        )

        self.in_range = []
        for x in range(7):
            self.in_range.append(
                self.generate_transaction(
                    self.budget, date=self.start.shift(days=x).datetime, amount=-100
                )
            )
        self.in_range.append(
            self.generate_transaction(
                self.budget, amount=100, date=self.start.shift(days=1), income=True
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
        budget_stats = data["budgets"][0]
        self.assertEqual(budget_stats["id"], self.budget.id)
        self.assertEqual(budget_stats["name"], self.budget.name)
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
            budget_stats["difference"], budget_stats["income"] + budget_stats["outcome"]
        )

    def test_get_stats(self):
        Transaction.objects.all().delete()
        tag1 = self.generate_tag()
        tag2 = self.generate_tag()
        self.generate_tag()  # unused

        tag1_trans = [
            self.generate_transaction(self.budget, amount=-100),
            self.generate_transaction(self.budget, amount=-100),
        ]
        tag2_trans = [self.generate_transaction(self.budget, amount=-100)]
        both = self.generate_transaction(self.budget, amount=-100)
        both.tags.set([tag1, tag2])
        for trans in tag1_trans:
            trans.tags.add(tag1)
        for trans in tag2_trans:
            trans.tags.add(tag2)

        r = self.get(self.url)
        self.assertEqual(r.status_code, 200, r.json())
        data = r.json()["tags"]

        self.assertEqual(len(data), 2)
        for stat in data:
            if stat["name"] == tag1.name:
                self.assertEqual(stat["total"], -300)
            elif stat["name"] == tag2.name:
                self.assertEqual(stat["total"], -200)
            else:
                self.fail("tag should not be in response")

        # ensuring that the list is ordered from most used tag to least
        self.assertGreater(data[0]["total"], data[1]["total"])


class UserRelatedModelViewSetMixin:
    model: Model
    serializer: Serializer
    paginated_response: bool

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
        r = r if not self.paginated_response else r["results"]
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
    paginated_response = False


class TagViewSetTestCase(UserRelatedModelViewSetMixin, BudgetTestCase):
    serializer = TagSerializer
    model = Tag
    paginated_response = True


class HealthCheck(BudgetTestCase):
    def test(self):
        r = self.get("/api/v2/health", user=None)
        self.assertEqual(r.status_code, 200)
