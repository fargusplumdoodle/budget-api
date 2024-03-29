from typing import Type, Union

import arrow
from django.contrib.auth.models import User
from django.core.serializers.base import Serializer
from django.db.models import Model
from rest_framework.reverse import reverse
from rest_framework.serializers import ModelSerializer

from api2.constants import DefaultTags, ROOT_BUDGET_NAME
from api2.models import Transaction, Budget, Tag, UserInfo
from api2.serializers import BudgetSerializer, TagSerializer, TransactionSerializer
from budget.utils.test import BudgetTestCase

now = arrow.get(2021, 1, 1)


class TransactionViewTestCase(BudgetTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.budgets = [
            cls.generate_budget(),
            cls.generate_budget(),
            cls.generate_budget(),
            cls.generate_budget(),
        ]
        cls.generate_transaction(
            cls.budgets[0],
            description="Will not show up anywhere",
            prediction=True,
        )

    def test_pagination_list(self):
        self.generate_transaction(budget=self.budgets[0])
        r = self.get(reverse("api2:transaction-list"))
        self.assertEqual(r.status_code, 200)
        paginated_response = r.json()
        self.assertIn("count", paginated_response)
        self.assertIn("next", paginated_response)
        self.assertIn("previous", paginated_response)
        self.assertIn("results", paginated_response)
        self.assertEqual(len(paginated_response["results"]), 1)

    def test_no_pagination_list(self):
        self.generate_transaction(budget=self.budgets[0])
        r = self.get(reverse("api2:transaction-list"), query={"no_pagination": "true"})
        self.assertEqual(r.status_code, 200)
        list_response = r.json()
        self.assertNotIn("count", list_response)
        self.assertNotIn("next", list_response)
        self.assertNotIn("previous", list_response)
        self.assertNotIn("results", list_response)
        self.assertEqual(len(list_response), 1)

    def test_excludes_filter(self):
        exclude_budget = self.budgets[0]

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
        include = self.generate_transaction(self.budgets[0], tags=[])
        self.generate_transaction(self.budgets[0], tags=[self.generate_tag()])
        r = self.get(
            reverse("api2:transaction-list"),
            query={"tags__none": True},
        )
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertLengthEqual(data["results"], 1)

        self.assertEqual(data["results"][0]["id"], include.id)

    def test_no_transactions_on_node_budgets(self):
        trans = self.generate_transaction(budget=self.budget_root)
        data = TransactionSerializer(trans).data
        r = self.post(
            reverse("api2:transaction-list"),
            data,
        )
        self.assertEqual(r.status_code, 400)


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
    detail_url: str

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user1 = cls.generate_user()
        cls.number_of_default_objects = cls.model.objects.filter(user=cls.user1).count()

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
        self.assertEqual(len(r), len(objs) + self.number_of_default_objects)

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


class BudgetViewSetTestCase(UserRelatedModelViewSetMixin, BudgetTestCase):
    serializer = BudgetSerializer
    model = Budget
    paginated_response = False
    ERRORS = BudgetSerializer.Errors

    def get_detail(self, budget: Budget):
        r = self.get(reverse(self.detail_url, (budget.id,)))
        self.assertEqual(r.status_code, 200)
        return r.json()

    def test_reject_updates_to_root_budget(self):
        budget = Budget.objects.get(user=self.user, name=ROOT_BUDGET_NAME)
        for request_method in [self.put, self.patch]:
            data = {"name": "name to reject"}
            r = request_method(
                reverse(self.detail_url, (budget.id,)), data, user=self.user
            )
            self.assertErrorInResponse(r, self.ERRORS.CANNOT_UPDATE_ROOT_BUDGET, 400)

    def test_cannot_turn_a_budget_into_a_node(self):
        non_node_budget = self.generate_budget()

        r = self.patch(
            reverse(self.detail_url, (non_node_budget.id,)),
            {"is_node": True},
            user=self.user,
        )
        self.assertErrorInResponse(r, self.ERRORS.CANNOT_MUTATE_IS_NODE, 400)

        non_node_budget.refresh_from_db()
        self.assertFalse(non_node_budget.is_node)

    def test_create_node_budget(self):
        node = self.generate_budget(is_node=True)
        Budget.objects.filter(pk=node.pk).delete()
        data = BudgetSerializer(node).data

        r = self.post(reverse(self.list_url), data, user=self.user)
        self.assertEqual(r.status_code, 201)
        is_node = Budget.objects.get(name=node.name).is_node
        self.assertTrue(is_node)

    def test_cannot_turn_a_node_budget_into_a_non_node(self):
        node_budget = self.generate_budget(is_node=True)

        r = self.patch(
            reverse(self.detail_url, (node_budget.id,)),
            {"is_node": False},
            user=self.user,
        )
        self.assertErrorInResponse(r, self.ERRORS.CANNOT_MUTATE_IS_NODE, 400)

        node_budget.refresh_from_db()
        self.assertTrue(node_budget.is_node)

    def test_can_only_assign_a_parent_to_a_node(self):
        non_node = self.generate_budget(is_node=False)
        budget_to_attempt_to_put_under_non_node = self.generate_budget(is_node=False)

        r = self.patch(
            reverse(self.detail_url, (budget_to_attempt_to_put_under_non_node.id,)),
            {"parent": non_node.id},
        )
        self.assertErrorInResponse(r, self.ERRORS.BUDGET_PARENTS_MUST_BE_NODES, 400)

    def test_node_budget_returns_the_balance_of_all_child_budgets(self):
        root, nodes, children = self.generate_budget_tree()
        [self.generate_transaction(child, amount=100) for child in children]

        for node in nodes:
            data = self.get_detail(node)
            self.assertEqual(data["balance"], 100 * 2)

        root_data = self.get_detail(root)
        self.assertEqual(root_data["balance"], 100 * 4)

    def test_node_budget_returns_the_allocation_of_all_child_budgets(self):
        root, nodes, children = self.generate_budget_tree()
        for child in children:
            child.monthly_allocation = 100
            child.save()

            data = self.get_detail(child)
            self.assertEqual(data["monthly_allocation"], 100 * 1)
            self.assertEqual(data["recursive_monthly_allocation"], 100 * 1)

        for node in nodes:
            data = self.get_detail(node)
            self.assertEqual(data["recursive_monthly_allocation"], 100 * 2)
            self.assertEqual(data["monthly_allocation"], 0)

        root_data = self.get_detail(root)
        self.assertEqual(root_data["monthly_allocation"], 0)
        self.assertEqual(root_data["recursive_monthly_allocation"], 100 * 4)


class TagViewSetTestCase(UserRelatedModelViewSetMixin, BudgetTestCase):
    serializer = TagSerializer
    model = Tag
    paginated_response = True

    def test_reject_updates_to_default_tags(self):
        for request_method in [self.put, self.patch]:
            for default_tag in DefaultTags.values():
                tag = Tag.objects.get(user=self.user, name=default_tag)
                data = {"name": "name to reject"}
                r = request_method(
                    reverse(self.detail_url, (tag.id,)), data, user=self.user
                )
                self.assertEqual(r.status_code, 400)

    def test_tag_names_are_case_insensitive_on_create(self):
        existing_tag = self.generate_tag()

        r = self.post(
            reverse(self.list_url), {"name": existing_tag.name.upper()}, user=self.user
        )

        self.assertEqual(r.status_code, 400)

    def test_tag_names_are_case_insensitive_on_update(self):
        existing_tag = self.generate_tag()
        tag_to_update = self.generate_tag()

        r = self.put(
            reverse(self.detail_url, (tag_to_update.id,)),
            {"name": existing_tag.name.upper()},
            user=self.user,
        )

        self.assertEqual(r.status_code, 400)


class HealthCheck(BudgetTestCase):
    def test(self):
        r = self.get("/api/v2/health", user=None)
        self.assertEqual(r.status_code, 200)


class UserInfoTestCase(BudgetTestCase):
    def setUp(self) -> None:
        UserInfo.objects.all().delete()

    def test_get(self):
        r = self.get(reverse("api2:info"))
        self.assertEqual(r.status_code, 200)

        data = r.json()
        self.assertEqual(data["expected_monthly_net_income"], 0)

    def test_put(self):
        new_info = {
            "expected_monthly_net_income": 100,
            "income_frequency_days": 13,
            "analyze_start": str(self.now.shift(months=3).date()),
            "predict_end": str(self.now.shift(months=4).date()),
            "theme": "CLASSIC",
            "darkMode": False,
        }
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
