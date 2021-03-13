from django.urls import path
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework_nested import routers

from api2.views import CreateAccountView
from . import views

app_name = "api2"
router = routers.DefaultRouter()
router.register("budget", views.BudgetViewset, "budget")
router.register("transaction", views.TransactionViewset, "transaction")

urlpatterns = [
    path("user/register", CreateAccountView.as_view(), name="register-user"),
    path("user/login", ObtainAuthToken.as_view(), name="login"),
]
urlpatterns += router.urls
