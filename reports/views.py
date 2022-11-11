from typing import Any, List

import arrow
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
    get_date_range,
    get_report_dates,
)
from reports.types import TimeBucketSizeOption, ReportGenerator, TimeRange


class ReportViewSet(ListModelMixin, GenericViewSet):
    model = Transaction
    filterset_class = TransactionFilterset
    report_generator: ReportGenerator

    def get_queryset(self):
        return self.model.objects.filter(budget__user=self.request.user)

    @staticmethod
    def validate(query_params: QueryDict):
        fields = [
            "time_bucket_size",
            "date__gte",
            "date__lte",
        ]
        for field in fields:
            if field not in query_params:
                raise ValidationError(f'Missing "{field}" query parameter')

    @staticmethod
    def get_time_bucket_size(query_params: QueryDict) -> str:
        if query_params["time_bucket_size"] not in TimeBucketSizeOption.values():
            raise ValidationError('Invalid "time_bucket_size" query parameter')

        return query_params["time_bucket_size"]

    @staticmethod
    def get_date(query_params: QueryDict, field_name: str) -> arrow.Arrow:
        try:
            date = arrow.get(query_params[field_name])
        except Exception:
            raise ValidationError(f'Invalid "{field_name}" query parameter')

        return date

    def get_budgets(self):
        budget_ids = self.request.GET.getlist("budget__includes")
        if budget_ids:
            return Budget.objects.filter(pk__in=budget_ids)
        return Budget.objects.filter()

    def get_tags(self):
        tag_ids = self.request.GET.getlist("tag__includes")
        if tag_ids:
            return Tag.objects.filter(pk__in=tag_ids, user=self.request.user)
        return Tag.objects.filter(user=self.request.user)

    @staticmethod
    def generate_report_bucket(
        transactions: QuerySet[Transaction], time_bucket: TimeRange
    ):
        raise NotImplementedError()

    @staticmethod
    def sum_transactions(transactions: QuerySet[Transaction], query: Q) -> int:
        return transactions.filter(query).aggregate(Sum("amount"))["amount__sum"] or 0

    def get_report_data(
        self, queryset: QuerySet[Transaction], time_buckets: List[TimeRange]
    ):
        return [
            self.generate_report_bucket(
                queryset.filter(date__range=get_date_range(time_range)), time_range
            )
            for time_range in time_buckets
        ]

    def list(self, request: Request, *args, **kwargs) -> Response:
        self.validate(request.GET)
        time_bucket_size = self.get_time_bucket_size(request.GET)
        queryset = self.filter_queryset(self.get_queryset())
        time_range = (
            self.get_date(request.GET, "date__gte"),
            self.get_date(request.GET, "date__lte"),
        )
        time_buckets = get_time_buckets(time_range, time_bucket_size)

        return Response(
            {
                "dates": get_report_dates(time_buckets),
                "data": self.get_report_data(queryset, time_buckets),
            }
        )


class MultiValuedReport(ReportViewSet):
    @classmethod
    def generate_report_bucket(cls, transactions, time_bucket) -> Any:
        return cls.sum_transactions(transactions, Q())

    def filter_queryset(self, queryset) -> QuerySet[Transaction]:
        return queryset


class BudgetReport(MultiValuedReport):
    @staticmethod
    def get_budget_and_children(budget: Budget):
        return Budget.objects.filter(parent=budget) if budget.is_node else [budget]


class TransactionCountReport(ReportViewSet):
    @staticmethod
    def generate_report_bucket(transactions: QuerySet[Transaction], time_bucket) -> Any:
        return transactions.count()


class IncomeReport(ReportViewSet):
    @classmethod
    def generate_report_bucket(cls, transactions, time_bucket) -> Any:
        return cls.sum_transactions(transactions, Q(income=True))


class BalanceReport(ReportViewSet):
    def filter_queryset(self, queryset) -> QuerySet[Transaction]:
        return queryset

    @classmethod
    def generate_report_bucket(cls, _, time_bucket) -> Any:
        return cls.sum_transactions(
            Transaction.objects.all(), Q(date__lte=time_bucket[1].datetime)
        )


class TransferReport(ReportViewSet):
    @classmethod
    def generate_report_bucket(cls, transactions, time_bucket) -> Any:
        return cls.sum_transactions(transactions, Q(transfer=True))


class OutcomeReport(ReportViewSet):
    @classmethod
    def generate_report_bucket(cls, transactions, time_bucket) -> Any:
        return cls.sum_transactions(transactions, Q(transfer=False, income=False))


class BudgetDeltaReport(BudgetReport):
    def get_report_data(
        self, queryset: QuerySet[Transaction], time_buckets: List[TimeRange]
    ):
        budgets = self.get_budgets()
        return {
            budget.id: [
                self.generate_report_bucket(
                    queryset.filter(
                        budget__in=self.get_budget_and_children(budget), date__range=get_date_range(time_range)
                    ),
                    time_range,
                )
                for time_range in time_buckets
            ]
            for budget in budgets
        }


class TagDeltaReport(MultiValuedReport):
    def get_report_data(
        self, queryset: QuerySet[Transaction], time_buckets: List[TimeRange]
    ):
        tags = self.get_tags()
        return {
            tag.id: [
                self.generate_report_bucket(
                    queryset.filter(tags=tag, date__range=get_date_range(time_range)),
                    time_range,
                )
                for time_range in time_buckets
            ]
            for tag in tags
        }


class BudgetBalanceReport(BudgetReport):
    def get_buckets_for_budget(
        self,
        budget: Budget,
        queryset: QuerySet[Transaction],
        time_buckets: List[TimeRange],
    ):
        budgets = self.get_budget_and_children(budget)
        return [
            self.generate_report_bucket(
                queryset.filter(budget__in=budgets, date__lte=time_range[1].datetime),
                time_range,
            )
            for time_range in time_buckets
        ]

    def get_report_data(
        self, queryset: QuerySet[Transaction], time_buckets: List[TimeRange]
    ):
        budgets = self.get_budgets()
        return {
            budget.id: self.get_buckets_for_budget(budget, queryset, time_buckets)
            for budget in budgets
        }


class TagBalanceReport(MultiValuedReport):
    def get_report_data(
        self, queryset: QuerySet[Transaction], time_buckets: List[TimeRange]
    ):
        tags = self.get_tags()
        return {
            tag.id: [
                self.generate_report_bucket(
                    queryset.filter(tags=tag, date__lte=time_range[1].datetime),
                    time_range,
                )
                for time_range in time_buckets
            ]
            for tag in tags
        }
