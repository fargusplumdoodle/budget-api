from typing import Any

from django.db.models import QuerySet, Sum, Q
from django.http import QueryDict
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import ListModelMixin
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api2.filters import TransactionFilterset
from api2.models import Transaction, Budget, Tag
from reports.time_buckets import (
    get_time_buckets,
    get_time_range,
    get_date_range,
    get_report_dates,
)
from reports.types import TimeBucketSizeOption, ReportGenerator


class ReportViewSet(ListModelMixin, GenericViewSet):
    model = Transaction
    filterset_class = TransactionFilterset
    report_generator: ReportGenerator

    def get_queryset(self):
        return self.model.objects.filter(budget__user=self.request.user)

    @staticmethod
    def get_time_bucket_size(query_params: QueryDict) -> str:
        if "time_bucket_size" not in query_params:
            raise ValidationError('Missing "time_bucket_size" query parameter')

        if query_params["time_bucket_size"] not in TimeBucketSizeOption.values():
            raise ValidationError('Invalid "time_bucket_size" query parameter')

        return query_params["time_bucket_size"]

    @staticmethod
    def generate_report(transactions: QuerySet[Transaction]) -> Any:
        raise NotImplementedError()

    @staticmethod
    def sum_transactions(transactions: QuerySet[Transaction], query: Q):
        return transactions.filter(query).aggregate(Sum("amount"))["amount__sum"]

    def list(self, request: Request, *args, **kwargs) -> Response:
        time_bucket_size = self.get_time_bucket_size(request.GET)
        queryset = self.filter_queryset(self.get_queryset())
        time_range = get_time_range(queryset)
        time_buckets = get_time_buckets(time_range, time_bucket_size)

        report_data = [
            self.generate_report(
                queryset.filter(date__range=get_date_range(time_range))
            )
            for time_range in time_buckets
        ]

        return Response(
            {
                "dates": get_report_dates(time_buckets),
                "data": report_data,
            }
        )


class TransactionCountReport(ReportViewSet):
    @staticmethod
    def generate_report(transactions: QuerySet[Transaction]) -> Any:
        return transactions.count()


class IncomeReport(ReportViewSet):
    @classmethod
    def generate_report(cls, transactions: QuerySet[Transaction]) -> Any:
        return cls.sum_transactions(transactions, Q(income=True))


class TransferReport(ReportViewSet):
    @classmethod
    def generate_report(cls, transactions: QuerySet[Transaction]) -> Any:
        return cls.sum_transactions(transactions, Q(transfer=True))


class OutcomeReport(ReportViewSet):
    @classmethod
    def generate_report(cls, transactions: QuerySet[Transaction]) -> Any:
        return cls.sum_transactions(transactions, Q(transfer=False, income=False))


class BudgetDeltaReport(ReportViewSet):
    @classmethod
    def generate_report(cls, transactions: QuerySet[Transaction]) -> Any:
        budgets = Budget.objects.filter(
            pk__in=transactions.values_list("budget", flat=True)
        )
        return {
            budget.name: cls.sum_transactions(transactions, Q(budget=budget))
            for budget in budgets
        }


class TagDeltaReport(ReportViewSet):
    @classmethod
    def generate_report(cls, transactions: QuerySet[Transaction]) -> Any:
        tags = Tag.objects.filter(pk__in=transactions.values_list("tags", flat=True))
        return {
            tag.name: cls.sum_transactions(transactions, Q(tags=tag)) for tag in tags
        }


class BudgetBalanceReport(ReportViewSet):
    """
    WARNING: THIS WILL NOT WORK IF PROVIDED FILTERS OTHER THAN BUDGET
    """

    @classmethod
    def generate_report(cls, transactions: QuerySet[Transaction]) -> Any:
        budgets = Budget.objects.filter(
            pk__in=transactions.values_list("budget", flat=True)
        )
        time_range = get_time_range(transactions)

        if not time_range:
            return {budget.name: 0 for budget in budgets}

        return {
            budget.name: cls.sum_transactions(
                Transaction.objects.all(),
                Q(budget=budget, date__lte=time_range[1].datetime),
            )
            for budget in budgets
        }


class TagBalanceReport(ReportViewSet):
    """
    WARNING: THIS WILL NOT WORK IF PROVIDED FILTERS OTHER THAN TAGS
    """

    @classmethod
    def generate_report(cls, transactions: QuerySet[Transaction]) -> Any:
        tags = Tag.objects.filter(pk__in=transactions.values_list("tags", flat=True))
        time_range = get_time_range(transactions)

        if not time_range:
            return {tag.name: 0 for tag in tags}

        return {
            tag.name: cls.sum_transactions(
                Transaction.objects.all(),
                Q(tags=tag, date__lte=time_range[1].datetime),
            )
            for tag in tags
        }
