from ynab.data.req import make_ynab_request
from ynab.data.types import Response


def get_budgets():
    response: Response = make_ynab_request("get", "/budgets")
    assert response.status_code == 200
    return response.data["data"]["budgets"]
