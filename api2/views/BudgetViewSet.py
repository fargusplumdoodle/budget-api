from rest_framework.permissions import IsAuthenticated

from .UserRelatedModelViewSet import UserRelatedModelViewSet
from ..filters import BudgetFilterset
from ..models import Budget
from ..serializers import BudgetSerializer


class BudgetViewset(UserRelatedModelViewSet):
    model = Budget
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    filterset_class = BudgetFilterset

    def get_queryset(self):
        return super().get_queryset().order_by("-monthly_allocation")
