import io

from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import TokenAuthentication

from api2.models import Budget, Transaction
from api2.serializers import (
    BudgetSerializer,
    TransactionSerializer,
    AddMoneySerializer,
    RegisterSerializer,
)
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
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class TransactionViewset(ModelViewSet):
    serializer_class = TransactionSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filterset_class = TransactionFilterset

    def get_queryset(self):
        return Transaction.objects.filter(budget__user=self.request.user).order_by(
            "-date"
        )

    @action(detail=False, methods=["post"])
    def income(self, request):
        """
        For adding money to all budgets

        returns a list of transactions
        """
        stream = io.BytesIO(request.body)
        data = JSONParser().parse(stream)

        serializer = AddMoneySerializer(data=data, many=False)
        serializer.is_valid(raise_exception=True)

        transactions = add_income(
            amount=serializer.validated_data["amount"],
            description=serializer.validated_data["description"],
            date=serializer.validated_data["date"],
            user=request.user,
            save=True,
        )

        serializer = TransactionSerializer(transactions, many=True)

        return Response(serializer.data, status=201, content_type="application/json")


class CreateAccountView(APIView):
    @csrf_exempt
    def post(self, request):
        """
        For creating accounts
        - Will be replaced by OAuth
        - does not validate login info such as password complexity

        Returns token for user

        """
        # Loading data
        stream = io.BytesIO(request.body)
        data = JSONParser().parse(stream)

        serializer = RegisterSerializer(data=data)

        if serializer.is_valid():

            # creating user
            user, created = User.objects.get_or_create(username=data.get("username"))
            user.set_password(data.get("password"))
            user.save()

            # creating token
            token, _ = Token.objects.get_or_create(user=user)

            # returning id to user
            return Response({"token": token.key}, status=201)
        else:
            return Response(serializer.errors, status=400)
