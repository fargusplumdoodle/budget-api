from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from ..filters import TransactionFilterset
from ..models import Transaction
from ..serializers import TransactionSerializer


class TransactionViewset(ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = TransactionFilterset

    def get_queryset(self):
        return Transaction.objects.filter(
            budget__user=self.request.user, prediction=False
        ).order_by("-date")
