from typing import Sized
from urllib.parse import urlencode

import arrow
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from api2.models import Budget, Transaction, Tag


class BudgetTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = cls.generate_user()
        cls.now = arrow.now()

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
        defaults = {
            "name": f"budget_{Budget.objects.count():07}",
            "percentage": 0,
            "initial_balance": 0,
        }
        if "user" not in kwargs:
            defaults["user"] = cls.user  # type: ignore

        defaults.update(kwargs)
        return Budget.objects.create(**defaults)

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

        if isinstance(defaults["date"], arrow.Arrow):
            defaults["date"] = defaults["date"].datetime

        tags = defaults.get("tags")
        if tags:
            del defaults["tags"]

        trans = Transaction.objects.create(**defaults)

        if tags:
            trans.tags.set(tags)

        return trans
