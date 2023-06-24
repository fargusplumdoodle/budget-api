from pydantic import BaseModel
from ynab.data import ynab


class YnabSettings(BaseModel):
    budget_id: str


def _build_settings():
    return YnabSettings(budget_id=ynab.get_budgets()[0]["id"])


_ynab_settings = None


def get_ynab_settings():
    global _ynab_settings
    if _ynab_settings is None:
        _ynab_settings = _build_settings()
    return _ynab_settings
