import io

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import TokenAuthentication

from api2.models import Budget, Transaction
from api2.serializers import BudgetSerializer, TransactionSerializer, AddMoneySerializer
from api2.filters import BudgetFilterset, TransactionFilterset
from api2.utils import add_income


class BudgetViewset(ModelViewSet):
    serializer_class = BudgetSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filterset_class = BudgetFilterset

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data={"user": request.user.pk, **request.data})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class TransactionViewset(ModelViewSet):
    serializer_class = TransactionSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filterset_class = TransactionFilterset

    def get_queryset(self):
        return Transaction.objects.filter(budget__user=self.request.user)

    @action(detail=False, methods=['post'])
    def income(self, request):
        """
        For adding money to all budgets

        returns a list of transactions
        """
        stream = io.BytesIO(request.body)
        data = JSONParser().parse(stream)

        serializer = AddMoneySerializer(data=data, many=False)
        serializer.is_valid(raise_exception=True)

        transactions = add_income(amount=serializer.validated_data['amount'], user=request.user, save=True)

        serializer = TransactionSerializer(transactions, many=True)

        return Response(serializer.data, status=201, content_type="application/json")
