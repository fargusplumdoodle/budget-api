from django.urls import path
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework_nested import routers

from api2.views import UserInfoView
from . import views

app_name = "api2"
router = routers.DefaultRouter()
router.register("budget", views.BudgetViewset, "budget")
router.register("transaction", views.TransactionViewset, "transaction")
router.register("tag", views.TagViewset, "tag")
router.register("report", views.ReportViewset, "report")

urlpatterns = [
    path("user/login", ObtainAuthToken.as_view(), name="login"),
    path("user/info", UserInfoView.as_view(), name="info"),
    path("health", views.HealthCheck.as_view()),
]
urlpatterns += router.urls
