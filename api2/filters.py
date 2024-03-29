from django.db.models import Count
from django_filters import rest_framework as filters, MultipleChoiceFilter
from django import forms


class CharListField(forms.MultipleChoiceField):
    """Remove validation from native MultipleChoiceField"""

    def validate(self, value):
        pass


class CharListFilter(MultipleChoiceFilter):
    """
    Accepts multiple values for the same key in the format ?n=v1&n=v2

    Behaves exactly like the MultipleChoiceFilter, except the `choices`
    parameter is no longer required. Forms the OR of the given values, unless
    the `conjoined=True` argument is given in which case AND will be used.
    """

    field_class = CharListField


class BudgetFilterset(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="exact")
    name__icontains = filters.CharFilter(field_name="name", lookup_expr="icontains")
    id = filters.NumberFilter(field_name="id")


class TransactionFilterset(filters.FilterSet):
    amount = filters.NumberFilter(field_name="amount")
    amount__gt = filters.NumberFilter(field_name="amount", lookup_expr="gt")
    amount__lt = filters.NumberFilter(field_name="amount", lookup_expr="lt")
    amount__gte = filters.NumberFilter(field_name="amount", lookup_expr="gte")
    amount__lte = filters.NumberFilter(field_name="amount", lookup_expr="lte")

    budget = filters.CharFilter(field_name="budget__id", lookup_expr="exact")
    budget__includes = CharListFilter(field_name="budget__id", lookup_expr="exact")
    budget__excludes = CharListFilter(
        field_name="budget__id", lookup_expr="exact", method="excludes"
    )
    budget__name__iexact = filters.CharFilter(
        field_name="budget__name", lookup_expr="iexact"
    )
    budget__name__icontains = filters.CharFilter(
        field_name="budget__name", lookup_expr="icontains"
    )

    description__iexact = filters.CharFilter(
        field_name="description", lookup_expr="iexact"
    )
    description__icontains = filters.CharFilter(
        field_name="description", lookup_expr="icontains"
    )

    date = filters.DateFilter(field_name="date")
    date__gt = filters.DateFilter(field_name="date", lookup_expr="gt")
    date__gte = filters.DateFilter(field_name="date", lookup_expr="gte")
    date__lt = filters.DateFilter(field_name="date", lookup_expr="lt")
    date__lte = filters.DateFilter(field_name="date", lookup_expr="lte")

    tags = CharListFilter(field_name="tags__name", lookup_expr="iexact")
    tags__includes = CharListFilter(field_name="tags__name", lookup_expr="iexact")
    tags__excludes = CharListFilter(
        field_name="tags__name", lookup_expr="exact", method="excludes"
    )
    tags__none = CharListFilter(
        field_name="tags", lookup_expr="exact", method="tags_none"
    )

    created = filters.DateTimeFilter(field_name="created")
    created__gt = filters.DateTimeFilter(field_name="created", lookup_expr="gt")
    created__gte = filters.DateTimeFilter(field_name="created", lookup_expr="gte")
    created__lt = filters.DateTimeFilter(field_name="created", lookup_expr="lt")
    created__lte = filters.DateTimeFilter(field_name="created", lookup_expr="lte")

    modified = filters.DateTimeFilter(field_name="modified")
    modified__gt = filters.DateTimeFilter(field_name="modified", lookup_expr="gt")
    modified__gte = filters.DateTimeFilter(field_name="modified", lookup_expr="gte")
    modified__lt = filters.DateTimeFilter(field_name="modified", lookup_expr="lt")
    modified__lte = filters.DateTimeFilter(field_name="modified", lookup_expr="lte")

    @staticmethod
    def excludes(queryset, name, value):
        return queryset.exclude(**{f"{name}__in": value})

    @staticmethod
    def tags_none(queryset, name, value):
        if not value:
            return queryset
        return queryset.annotate(tag_count=Count("tags")).filter(tag_count=0)


class TagFilterset(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="exact")
    name__icontains = filters.CharFilter(field_name="name", lookup_expr="icontains")
