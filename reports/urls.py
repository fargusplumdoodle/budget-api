from rest_framework_nested import routers

from . import views

app_name = "reports"
router = routers.DefaultRouter()
router.register(
    "transaction_counts", views.TransactionCountReport, "transaction_counts"
)

urlpatterns = router.urls
