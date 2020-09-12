from django.urls import path
import django.contrib.auth.views as login_view
from web.views import dashboard, budget, add_money, graph_history_page, add_transaction

app_name = 'web'


urlpatterns = [
    path("budget/<str:budget_name>/", budget, name='budget'),
    path("add_money/", add_money, name='add_money'),
    path("add_transaction/", add_transaction, name='add_transaction'),
    path("", dashboard, name='dashboard'),
    path("login/", login_view.LoginView.as_view(template_name="api/login.html"), name='login'),
    path("logout/", login_view.LogoutView.as_view(template_name="api/login.html"), name='logout'),
    path("graph_history", graph_history_page, name='graph_history'),
]
