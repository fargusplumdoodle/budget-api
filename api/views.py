# from rest_framework.response import Response
# from rest_framework.views import APIView
from django.shortcuts import render, get_object_or_404
from .models import Budget
from .helper import budgets_sum_to_one


def dashboard(request):
    context = {}

    context["budgets"] = Budget.objects.all()
    context["budget_balanced"] = budgets_sum_to_one()

    return render(request, "api/index.html", context=context)


def budget(request, budget_name):

    budget = get_object_or_404(Budget, name=budget_name)

    context = {'budget': budget}

    return render(request, "api/budgets/budget.html", context=context)
