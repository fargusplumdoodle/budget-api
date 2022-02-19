from typing import List, Dict, Callable

from django.db.models import QuerySet
from django.http import QueryDict
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import ListModelMixin
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from api2.filters import TransactionFilterset
from api2.models import Transaction
from reports.time_buckets import (
    get_time_buckets,
    get_time_range,
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
    def get_time_bucket_size(query_params: QueryDict) -> str:
        if "time_bucket_size" not in query_params:
            raise ValidationError('Missing "time_bucket_size" query parameter')

        if query_params["time_bucket_size"] not in TimeBucketSizeOption.values():
            raise ValidationError('Invalid "time_bucket_size" query parameter')

        return query_params["time_bucket_size"]

    @staticmethod
    def generate_report(transactions: QuerySet[Transaction]) -> int:
        raise NotImplementedError()

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
    def generate_report(transactions: QuerySet[Transaction]) -> int:
        return transactions.count()
