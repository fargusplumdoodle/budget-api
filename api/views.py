# from rest_framework.response import Response
# from rest_framework.views import APIView
from django.shortcuts import render, get_object_or_404
from .models import Budget, Transaction
from .helper import budgets_sum_to_one

SIDEBAR_LINKS = [
    ('Add transaction', '/admin/api/transaction/add/'),
    ('Admin page', '/admin/'),
]


def dashboard(request):
    context = {}

    context["budget_list"] = Budget.objects.all()
    context["budget_balanced"] = budgets_sum_to_one()

    context['trans_list'] = Transaction.objects.order_by('date')[::-1][:10]

    return render(request, "api/index.html", context=context)


def budget(request, budget_name):
    budget = get_object_or_404(Budget, name=budget_name)

    context = {
        'budget': budget,
        'trans_list': Transaction.objects.filter(budget=budget).order_by('date')[::-1][:10]
    }


    return render(request, "api/budgets/templates/api/budget.html", context=context)
