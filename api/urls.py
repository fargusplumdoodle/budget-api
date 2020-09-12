from django.urls import path

from api.views.budget import BudgetView, BudgetTransactionView
from api.views.transaction import AddTransactionView, AddMoneyView
from web.views import GraphBudgetHistory
from api.views.account import CreateAccountView, ObtainAuthToken

app_name = 'api'

urlpatterns = [
    path("user/register", CreateAccountView.as_view(), name="register-user"),
    path("user/login", ObtainAuthToken.as_view(), name="login"),
    path("graph/history", GraphBudgetHistory.as_view(), name='api_graph_history'),
    path("budget", BudgetView.as_view(), name='budgets'),
    path("budget/<int:budget_id>", BudgetTransactionView.as_view(), name='budget_transaction'),
    path("transaction", AddTransactionView.as_view(), name='add_transaction'),
    path("add_money", AddMoneyView.as_view(), name='add_money'),
]
