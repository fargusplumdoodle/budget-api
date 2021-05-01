import io
import operator

from django.contrib.auth.models import User
from django.db.models import Model, Q, Sum, QuerySet
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import TokenAuthentication

from api2.models import Budget, Transaction, Tag
from api2.serializers import (
    BudgetSerializer,
    TransactionSerializer,
    AddMoneySerializer,
    RegisterSerializer,
    TagSerializer,
)
from api2.filters import BudgetFilterset, TransactionFilterset, TagFilterset
from api2.utils import add_income


class UserRelatedModelViewSet(ModelViewSet):
    model: Model

    def create(self, request, *args, **kwargs):
        request.data.update({**request.data, "user": request.user.pk})
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        request.data.update({**request.data, "user": request.user.pk})
        return super().update(request, *args, **kwargs)

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class BudgetViewset(UserRelatedModelViewSet):
    model = Budget
    serializer_class = BudgetSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filterset_class = BudgetFilterset

    def get_queryset(self):
        return super().get_queryset().order_by("-percentage")


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


class TagViewset(UserRelatedModelViewSet):
    model = Tag
    serializer_class = TagSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filterset_class = TagFilterset


class ReportViewset(ModelViewSet):
    serializer_class = TransactionSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filterset_class = TransactionFilterset

    def get_queryset(self):
        return Transaction.objects.filter(budget__user=self.request.user).order_by(
            "-date"
        )

    @staticmethod
    def get_budget_stats(qs: QuerySet) -> list:
        if len(qs) == 0:
            return []

        budgets = Budget.objects.filter(id__in=set(qs.values_list("budget", flat=True)))
        start_date = qs.last().date
        end_date = qs.first().date
        date_range = (start_date, end_date)

        stats = []
        for budget in budgets:
            budget_stats = {
                "id": budget.id,
                "name": budget.name,
                "initial_balance": budget.balance(Q(date__lt=start_date)),
                "final_balance": budget.balance(Q(date__lte=end_date)),
                "income": Transaction.objects.filter(
                    budget=budget, date__range=date_range, income=True
                ).aggregate(total=Sum("amount"))["total"]
                or 0,
                "outcome": Transaction.objects.filter(
                    budget=budget, date__range=date_range, income=False
                ).aggregate(total=Sum("amount"))["total"]
                or 0,
            }
            budget_stats["difference"] = (
                budget_stats["income"] + budget_stats["outcome"]
            )
            stats.append(budget_stats)

        return stats

    @staticmethod
    def get_tag_stats(qs: QuerySet) -> list:
        stats = []
        if len(qs) == 0:
            return stats

        tags = Tag.objects.filter(user=qs.first().budget.user)
        for tag in tags:
            transactions_with_tag = qs.filter(tags=tag)
            if len(transactions_with_tag) == 0:
                continue
            total = transactions_with_tag.aggregate(total=Sum("amount"))["total"]
            stats.append({"name": tag.name, "total": total})

        stats.sort(key=operator.itemgetter("total"), reverse=True)
        return stats

    def list(self, request, **kwargs):
        qs = self.filter_queryset(self.get_queryset())

        response = {
            "transactions": self.serializer_class(qs, many=True).data,
            "budgets": {},
            "tags": self.get_tag_stats(qs),
        }

        if request.GET.get("date__gte") and request.GET.get("date__lte"):
            response["budgets"] = self.get_budget_stats(qs)

        return Response(response)


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
