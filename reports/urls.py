from rest_framework_nested import routers

from . import views

app_name = "reports"
router = routers.DefaultRouter()
router.register(
    "transaction_counts", views.TransactionCountReport, "transaction_counts"
)
router.register("income", views.IncomeReport, "income")
router.register("transfer", views.TransferReport, "transfer")
router.register("outcome", views.OutcomeReport, "outcome")
router.register("balance", views.BalanceReport, "balance")
router.register(
    "budget_delta",
    views.BudgetDeltaReport,
    "budget_delta",
)
router.register(
    "budget_income",
    views.BudgetIncomeReport,
    "budget_income",
)
router.register(
    "budget_outcome",
    views.BudgetOutcomeReport,
    "budget_outcome",
)
router.register(
    "budget_balance",
    views.BudgetBalanceReport,
    "budget_balance",
)
router.register(
    "tag_balance",
    views.TagBalanceReport,
    "tag_balance",
)
router.register(
    "tag_delta",
    views.TagDeltaReport,
    "tag_delta",
)

urlpatterns = router.urls
