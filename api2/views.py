import io
import operator
from typing import Type, List, Dict

from django.db.models import Model, Q, Sum, QuerySet
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from api2.models import Budget, Transaction, Tag, UserInfo
from api2.serializers import (
    BudgetSerializer,
    TransactionSerializer,
    AddMoneySerializer,
    TagSerializer,
    UserInfoSerializer,
)
from api2.filters import BudgetFilterset, TransactionFilterset, TagFilterset
from api2.utils import add_monthly_income


class HealthCheck(APIView):
    @staticmethod
    def get(request: Request):
        return Response(status=200)


class UserRelatedModelViewSet(ModelViewSet):
    model: Type[Model]

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
    permission_classes = [IsAuthenticated]
    pagination_class = None
    filterset_class = BudgetFilterset

    def get_queryset(self):
        return super().get_queryset().order_by("-monthly_allocation")


class TransactionViewset(ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = TransactionFilterset

    def get_queryset(self):
        return Transaction.objects.filter(
            budget__user=self.request.user, prediction=False
        ).order_by("-date")


class TagViewset(UserRelatedModelViewSet):
    model = Tag
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = TagFilterset

    def get_queryset(self):
        return Tag.objects.filter(user=self.request.user)


class ReportViewset(ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = TransactionFilterset

    def get_queryset(self):
        return Transaction.objects.filter(
            budget__user=self.request.user, prediction=False
        ).order_by("-date")

    @staticmethod
    def get_budget_stats(qs: QuerySet[Transaction]) -> list:
        if len(qs) == 0:
            return []

        budgets = Budget.objects.filter(id__in=set(qs.values_list("budget", flat=True)))
        first_trans = qs.first()
        last_trans = qs.last()
        assert first_trans and last_trans
        start_date = last_trans.date
        end_date = first_trans.date
        date_range = (start_date, end_date)

        stats = []
        for budget in budgets:
            budget_stats = {
                "id": budget.id,
                "name": budget.name,
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
                budget_stats["income"] + budget_stats["outcome"]  # type: ignore
            )
            stats.append(budget_stats)

        return stats

    @staticmethod
    def get_tag_stats(qs: QuerySet) -> list:
        stats: List[Dict[str, str]] = []
        if len(qs) == 0:
            return stats
        first_trans = qs.first()
        assert first_trans
        tags = Tag.objects.filter(user=first_trans.budget.user)
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


class UserInfoView(APIView):
    model = UserInfo
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        info, _ = self.model.objects.get_or_create(user=request.user)
        return Response(data=UserInfoSerializer(info).data, status=200)

    def put(self, request: Request):
        info, _ = self.model.objects.get_or_create(user=request.user)

        stream = io.BytesIO(request.body)
        data = JSONParser().parse(stream)

        serializer = UserInfoSerializer(info, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=serializer.data, status=201)
