from django_filters import rest_framework as filters


class BudgetFilterset(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="exact")
    name__icontains = filters.CharFilter(field_name="name", lookup_expr="icontains")
    id = filters.NumberFilter(field_name="id")


class TransactionFilterset(filters.FilterSet):
    amount__eq = filters.NumberFilter(field_name="amount")
    amount__gt = filters.NumberFilter(field_name="amount", lookup_expr="gt")
    amount__lt = filters.NumberFilter(field_name="amount", lookup_expr="lt")

    budget = filters.CharFilter(field_name="budget__id", lookup_expr="exact")
    budget__name = filters.CharFilter(field_name="budget__name", lookup_expr="exact")

    description__exact = filters.CharFilter(field_name="description", lookup_expr="exact")
    description__icontains = filters.CharFilter(field_name="description", lookup_expr="icontains")

    date = filters.DateFilter(field_name="date")
    date__gt = filters.DateFilter(field_name="date", lookup_expr="gt")
    date__lt = filters.DateFilter(field_name="date", lookup_expr="lt")

