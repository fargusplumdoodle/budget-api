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
    amount__eq = filters.NumberFilter(field_name="amount")
    amount__gt = filters.NumberFilter(field_name="amount", lookup_expr="gt")
    amount__lt = filters.NumberFilter(field_name="amount", lookup_expr="lt")

    budget = filters.CharFilter(field_name="budget__id", lookup_expr="exact")
    budget__name = filters.CharFilter(field_name="budget__name", lookup_expr="exact")

    description__exact = filters.CharFilter(
        field_name="description", lookup_expr="exact"
    )
    description__icontains = filters.CharFilter(
        field_name="description", lookup_expr="icontains"
    )

    date = filters.DateFilter(field_name="date")
    date__gte = filters.DateFilter(field_name="date", lookup_expr="gte")
    date__lte = filters.DateFilter(field_name="date", lookup_expr="lte")

    tags = CharListFilter(field_name="tags__name", lookup_expr="iexact")


class TagFilterset(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="exact")
    name__icontains = filters.CharFilter(field_name="name", lookup_expr="icontains")
