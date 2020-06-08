from django.urls import path, include

from api.views.budget import BudgetView
from web.views import GraphBudgetHistory
from api.views.account import CreateAccountView, ObtainAuthToken

urlpatterns = [
    path("user/register", CreateAccountView.as_view(), name="register-user"),
    path("user/login", ObtainAuthToken.as_view(), name="login"),
    path("graph/history", GraphBudgetHistory.as_view(), name='api_graph_history'),
    path("budget", BudgetView.as_view(), name='budgets'),
]
