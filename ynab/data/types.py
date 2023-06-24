import json
from typing import Optional, Union, List, Any

from pydantic import BaseModel


class YnabException(Exception):
    pass


TransactionType = Union["uncategorized", "unapproved"]


class Response(BaseModel):
    status_code: int
    data: dict
    source: str
    method: str
    url: str

    @classmethod
    def from_requests_response(cls, response):
        return cls(
            status_code=response.status_code,
            data=response.json(),
            source="ynab",
            method=response.request.method.lower(),
            url=response.request.url,
        )

    @property
    def is_success(self):
        return 200 <= self.status_code < 300

    def format(self):
        return json.dumps(self.dict(), indent=2)


class Category(BaseModel):
    id: str
    category_group_id: str
    category_group_name: str
    name: str
    hidden: bool
    original_category_group_id: Optional[str] = None
    note: Optional[str] = None
    budgeted: int
    activity: int
    balance: int
    goal_type: Optional[str] = None
    goal_day: Optional[str] = None
    goal_cadence: Optional[str] = None
    goal_cadence_frequency: Optional[str] = None
    goal_creation_month: Optional[str] = None
    goal_target: int
    goal_target_month: Optional[str] = None
    goal_percentage_complete: Optional[int] = None
    goal_months_to_budget: Optional[int] = None
    goal_under_funded: Optional[int] = None
    goal_overall_funded: Optional[int] = None
    goal_overall_left: Optional[int] = None
    deleted: bool


class Payee(BaseModel):
    id: str
    name: str
    transfer_account_id: Optional[str]
    deleted: bool


class Transaction(BaseModel):
    id: str
    date: str  # If you want to validate this field as a date, use date: datetime.date from Python's datetime module
    amount: int
    memo: Optional[str]
    cleared: str
    approved: bool
    flag_color: Optional[str]
    account_id: str
    account_name: str
    payee_id: Optional[str]
    payee_name: Optional[str]
    category_id: Optional[str]
    category_name: str
    transfer_account_id: Optional[str]
    transfer_transaction_id: Optional[str]
    matched_transaction_id: Optional[str]
    import_id: Optional[str]
    import_payee_name: Optional[str]
    import_payee_name_original: Optional[str]
    debt_transaction_type: Optional[str]
    deleted: bool
    subtransactions: List
