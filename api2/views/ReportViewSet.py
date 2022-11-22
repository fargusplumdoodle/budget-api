import operator
from typing import List, Dict

from django.db.models import QuerySet, Sum
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from ..filters import TransactionFilterset
from ..models import Transaction, Budget, Tag
from ..serializers import TransactionSerializer


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
                "final_balance": budget.balance(),
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
