from typing import List, Optional

from arrow import Arrow
from pydantic import BaseModel

from ynab.data.req import make_ynab_request
from ynab.data.types import Response, Category, Payee, TransactionType, Transaction

TEST_BUDGET_ID = "d87689f7-f450-4fa0-99ec-b590c7bf3494"
PROD_BUDGET_ID = "e6c14005-8892-49f8-9ab5-3bc5c8fe3d8c"

"""
Implementing:
https://api.youneedabudget.com/v1#/
"""


class _YnabBase(BaseModel):
    budget_id: str = PROD_BUDGET_ID


class _BudgetsMixin(_YnabBase):
    @staticmethod
    def get_budgets():
        response: Response = make_ynab_request("get", "/budgets")
        return response.data["data"]["budgets"]


class _PayeesMixin(_YnabBase):
    def get_payees(self) -> List[Payee]:
        response: Response = make_ynab_request("get", f"/budgets/{self.budget_id}/payees")
        return [Payee(**payee) for payee in response.data["data"]["payees"]]


class _MonthMixin(_YnabBase):
    def get_months(self):
        uri = f"/budgets/{self.budget_id}/months"
        response = make_ynab_request("get", uri)
        print(response.format())


class _CategoryMixin(_YnabBase):
    def get_categories(self) -> List[Category]:
        uri = f"/budgets/{self.budget_id}/categories"
        response: Response = make_ynab_request("get", uri)
        groups = response.data["data"]["category_groups"]
        categories: List[Category] = []
        for group in groups:
            for category in group["categories"]:
                categories.append(Category(**category))
        return categories

    def get_category(self, id: str) -> Category:
        uri = f"/budgets/{self.budget_id}/categories/{id}"
        response: Response = make_ynab_request("get", uri)
        return Category(**response.data["data"]["category"])

    def get_category_for_month(self, id: str, date: Arrow) -> Category:
        uri = f"/budgets/{self.budget_id}/months/{date.format('YYYY-MM-DD')}/categories/{id}"
        response: Response = make_ynab_request("get", uri)
        return Category(**response.data["data"]["category"])


class _TransactionMixin(_YnabBase):
    def get_transactions(self, since_date: Arrow = None, trans_type: Optional[TransactionType] = None):
        uri = f"/budgets/{self.budget_id}/transactions"
        params = {}
        if since_date:
            params["since_date"] = since_date.format("YYYY-MM-DD")
        if trans_type:
            params["type"] = trans_type

        response: Response = make_ynab_request("get", uri, params=params)
        return [Transaction(**transaction) for transaction in response.data["data"]["transactions"]]


class Ynab(_BudgetsMixin, _CategoryMixin, _PayeesMixin, _MonthMixin, _TransactionMixin):
    pass
