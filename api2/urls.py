from rest_framework_nested import routers

from . import views

router = routers.DefaultRouter()
router.register('budget', views.BudgetViewset, 'budget')
router.register('transaction', views.TransactionViewset, 'transaction')

urlpatterns = router.urls
