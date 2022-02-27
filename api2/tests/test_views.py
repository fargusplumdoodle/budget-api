from typing import Type, Union

import arrow
from django.contrib.auth.models import User
from django.core.serializers.base import Serializer
from django.db.models import Model, Q
from rest_framework.reverse import reverse
from rest_framework.serializers import ModelSerializer

from api2.models import Transaction, Budget, Tag, UserInfo
from api2.serializers import BudgetSerializer, TagSerializer
from budget.utils.test import BudgetTestCase

now = arrow.get(2021, 1, 1)


class TransactionViewTestCase(BudgetTestCase):
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

    def test_pagination_list(self):
        self.generate_transaction(budget=self.budgets_with_percentage[0])
        r = self.get(reverse("api2:transaction-list"))
        self.assertEqual(r.status_code, 200)
        paginated_response = r.json()
        self.assertIn("count", paginated_response)
        self.assertIn("next", paginated_response)
        self.assertIn("previous", paginated_response)
        self.assertIn("results", paginated_response)
        self.assertEqual(len(paginated_response["results"]), 1)

    def test_no_pagination_list(self):
        self.generate_transaction(budget=self.budgets_with_percentage[0])
        r = self.get(reverse("api2:transaction-list"), query={"no_pagination": "true"})
        self.assertEqual(r.status_code, 200)
        list_response = r.json()
        self.assertNotIn("count", list_response)
        self.assertNotIn("next", list_response)
        self.assertNotIn("previous", list_response)
        self.assertNotIn("results", list_response)
        self.assertEqual(len(list_response), 1)

    def test_excludes_filter(self):
        exclude_budget = self.budgets_with_percentage[0]

        for budget in Budget.objects.all():
            self.generate_transaction(budget=budget)

        r = self.get(
            reverse("api2:transaction-list"),
            query={"budget__excludes": exclude_budget.id},
        )

        self.assertEqual(r.status_code, 200)
        data = r.json()
        for transaction in data["results"]:
            self.assertNotEqual(transaction["budget"], exclude_budget.id)

    def test_no_tags_filter(self):
        include = self.generate_transaction(self.budgets_with_percentage[0], tags=[])
        self.generate_transaction(
            self.budgets_with_percentage[0], tags=[self.generate_tag()]
        )
        r = self.get(
            reverse("api2:transaction-list"),
            query={"tags__none": True},
        )
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertLengthEqual(data["results"], 1)

        self.assertEqual(data["results"][0]["id"], include.id)


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
    model: Type[Model]
    serializer: Type[Union[Serializer, ModelSerializer]]
    paginated_response: bool
    user: User

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user1 = cls.generate_user()

        reverse_url = "api2:" + cls.model.__name__.lower()
        cls.detail_url = reverse_url + "-detail"
        cls.list_url = reverse_url + "-list"

    @classmethod
    def generate_obj(cls, user: User, **kwargs):
        generator = getattr(cls, f"generate_{cls.model.__name__.lower()}")
        return generator(user=user, **kwargs)

    def test_get_list(self):
        objs = []
        for _ in range(10):
            objs.append(self.generate_obj(self.user))

        # wont show up
        self.generate_obj(self.generate_user())

        r = self.get(reverse(self.list_url), user=self.user).json()
        r = r if not self.paginated_response else r["results"]
        self.assertEqual(len(r), len(objs))

        for obj in r:
            self.assertTrue(
                self.model.objects.filter(id=obj["id"], user=self.user.id).exists()
            )

    def test_get_detail(self):
        obj = self.generate_obj(self.user)
        r = self.get(reverse(self.detail_url, (obj.id,)), user=self.user).json()
        self.assertEqual(r["id"], obj.id)
        if hasattr(obj, "name"):
            self.assertEqual(r["name"], obj.name)

    def test_create(self):
        obj = self.generate_obj(self.user)
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
        obj = self.generate_obj(self.user)
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
        obj = self.generate_obj(self.user)
        data = self.serializer(obj).data
        obj.delete()

        del data["id"]
        data["user"] = self.user1.id

        r = self.post(reverse(self.list_url), data, user=self.user).json()
        self.assertTrue(self.model.objects.filter(id=r["id"], user=self.user).exists())

    def test_create_unique_name_and_user(self):
        obj = self.generate_obj(self.user)
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

    def test_list_returns_object_in_order_most_frequent_to_least_frequent(self):
        if not (hasattr(self.model, "rank")):
            return

        expected_id_order = [
            self.generate_obj(self.user, rank=10).id,
            self.generate_obj(self.user, rank=2, name="a").id,
            self.generate_obj(self.user, rank=2, name="b").id,
        ]

        r = self.get(reverse(self.list_url), user=self.user)
        self.assertEqual(r.status_code, 200)

        data = r.json()
        object_list = data["results"] if self.paginated_response else data
        id_order = [obj["id"] for obj in object_list]
        self.assertEqual(id_order, expected_id_order)


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


class UserInfoTestCase(BudgetTestCase):
    def test_get(self):
        r = self.get(reverse("api2:info"))
        self.assertEqual(r.status_code, 200)

        data = r.json()
        self.assertEqual(data["expected_monthly_net_income"], 0)

    def test_put(self):
        new_info = {"expected_monthly_net_income": 100}
        r = self.put(reverse("api2:info"), data=new_info)
        self.assertEqual(r.status_code, 201)

        data = r.json()
        self.assertEqual(data, new_info)
        self.assertTrue(
            UserInfo.objects.filter(
                user=self.user, expected_monthly_net_income=100
            ).exists()
        )

    def test_put_invalid(self):
        new_info = {"expected_monthly_net_income": "bad data"}
        r = self.put(reverse("api2:info"), data=new_info)
        self.assertEqual(r.status_code, 400)
