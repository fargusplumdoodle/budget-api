from typing import Sized, List
from urllib.parse import urlencode

import arrow
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from api2.constants import ROOT_BUDGET_NAME
from api2.models import Budget, Transaction, Tag, UserInfo
from budget.utils.dates import nativify_dates


class BudgetTestCase(APITestCase):
    user: User
    user_info: UserInfo
    now: arrow.Arrow

    @classmethod
    def setUpTestData(cls):
        cls.user = cls.generate_user()
        cls.now = arrow.now()
        cls.user_info = UserInfo.objects.get(user=cls.user)
        cls.budget_root = Budget.objects.get(user=cls.user, name=ROOT_BUDGET_NAME)

    def _make_request(
        self, method_name, endpoint, data, encoding="json", query=None, user=None
    ):
        """Make a generic http request using the test client"""
        http_method = getattr(self.client, method_name)
        token, _ = Token.objects.get_or_create(user=user or self.user)

        if query is not None:
            endpoint += "?" + urlencode(query)

        return http_method(
            endpoint, data=data, format=encoding, HTTP_AUTHORIZATION=f"Token {token}"
        )

    def get(self, endpoint, query=None, user=None):
        return self._make_request("get", endpoint, None, "json", query, user)

    def head(self, endpoint, query=None, user=None):
        return self._make_request("head", endpoint, None, "json", query, user)

    def delete(self, endpoint, query=None, user=None):
        return self._make_request("delete", endpoint, None, "json", query, user)

    def post(self, endpoint, data, encoding="json", query=None, user=None):
        return self._make_request("post", endpoint, data, encoding, query, user)

    def put(self, endpoint, data, encoding="json", query=None, user=None):
        return self._make_request("put", endpoint, data, encoding, query, user)

    def patch(self, endpoint, data, encoding="json", query=None, user=None):
        return self._make_request("patch", endpoint, data, encoding, query, user)

    def assertLengthEqual(self, first: Sized, second: int) -> None:
        self.assertEqual(len(first), second)  # type: ignore

    @classmethod
    def generate_user(cls, **kwargs):
        defaults = {"username": f"user_{User.objects.count():07}"}
        defaults.update(kwargs)
        return User.objects.create(**defaults)

    @classmethod
    def generate_budget(cls, **kwargs):
        if "user" not in kwargs:
            kwargs["user"] = cls.user  # type: ignore

        if "parent" not in kwargs:
            kwargs["parent"] = Budget.objects.get(
                user=kwargs["user"], name=ROOT_BUDGET_NAME
            )

        defaults = {
            "name": f"budget_{Budget.objects.count():07}",
            "monthly_allocation": 0,
            **kwargs,
        }
        return Budget.objects.create(**defaults)

    @classmethod
    def generate_user_info(cls, **kwargs):
        defaults = {
            "user": cls.user,
            "expected_monthly_net_income": 300,
            "income_frequency_days": 14,
            "analyze_start": cls.now.shift(months=-3),
            "predict_end": cls.now.shift(months=3),
        }
        defaults.update(kwargs)
        defaults = nativify_dates(defaults)
        return UserInfo.objects.create(**defaults)

    @classmethod
    def generate_tag(cls, **kwargs):
        defaults = {"name": f"tag_{Tag.objects.count():07}", "rank": 0}
        if "user" not in kwargs:
            defaults["user"] = cls.user  # type: ignore

        defaults.update(kwargs)
        return Tag.objects.create(**defaults)

    @classmethod
    def generate_transaction(cls, budget: Budget, **kwargs):
        num_transactions = Transaction.objects.count()
        defaults = {
            "amount": num_transactions * 100,
            "description": f"trans: {num_transactions}",
            "budget": budget,
            "date": arrow.now().date(),
            "income": False,
            "transfer": False,
        }
        defaults.update(kwargs)
        defaults = nativify_dates(defaults)

        tags: List[Tag] = defaults.get("tags")  # type: ignore
        if tags is not None:
            del defaults["tags"]

        trans = Transaction.objects.create(**defaults)

        if tags:
            trans.tags.set(tags)

        return trans
