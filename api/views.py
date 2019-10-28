# from rest_framework.response import Response
# from rest_framework.views import APIView
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Budget, Transaction
from .helper import budgets_sum_to_one, add_money as add_money_function
from .forms import AddMoneyForm
from budget import settings


def dashboard(request):

    # x will be a redirect to the login page if the user is not authenticated
    x = verify_user(request)
    if x:
        return x

    context = {}

    context["budget_list"] = Budget.objects.all()
    context["budget_balanced"] = budgets_sum_to_one()

    context["total_money"] = "%.2f" % float(sum([x.amount for x in Transaction.objects.all()]) + sum([x.initial_balance for x in context['budget_list']]))

    context["trans_list"] = Transaction.objects.order_by("date")[::-1][:10]

    return render(
        request, "api/index.html", context=add_sidebar_context(context, request)
    )


def budget(request, budget_name):
    # x will be a redirect to the login page if the user is not authenticated
    x = verify_user(request)
    if x:
        return x
    budget = get_object_or_404(Budget, name=budget_name)

    context = {
        "budget": budget,
        "trans_list": Transaction.objects.filter(budget=budget).order_by("date")[::-1][
            :10
        ],
    }

    return render(
        request, "api/budget.html", context=add_sidebar_context(context, request)
    )


def add_money(request):
    # x will be a redirect to the login page if the user is not authenticated
    x = verify_user(request)
    if x:
        return x
    # adding form to context
    context = {"add_money_form": AddMoneyForm}

    if request.method == "POST":
        form = AddMoneyForm(request.POST)

        if form.is_valid():
            # attempting to add amount
            try:
                # adding money, getting transaction list
                transactions = add_money_function(form.cleaned_data.get("amount"))

                # adding trans list to show to the user
                context["trans_list"] = transactions

                messages.success(
                    request, f'Added {form.cleaned_data.get("amount")} to budgets!'
                )
                # if ANYTHING went wrong here, let them know
            except AssertionError:
                messages.warning(
                    request,
                    f'Failed to add {form.cleaned_data.get("amount")}, budget imbalanced. Balance your budget first',
                )
            except:
                messages.warning(
                    request, f'Failed to add {form.cleaned_data.get("amount")}'
                )
        else:
            messages.warning(request, f"Invalid input")

        return render(
            request, "api/add_money.html", context=add_sidebar_context(context, request)
        )
    else:
        # returning a regular page
        return render(
            request, "api/add_money.html", context=add_sidebar_context(context, request)
        )


def add_sidebar_context(context, request):
    # x will be a redirect to the login page if the user is not authenticated
    x = verify_user(request)
    if x:
        return x
    """
    Takes your current context and adds the sidebar information to it
    :param context: current context info for page
    :return: context with sidebar information and your existing info
    """
    sidebar_context = {
        "budget_balanced": budgets_sum_to_one(),
        "sidebar": [
            ("Add transaction", "/admin/api/transaction/add/"),
            ("View Budgets", "/admin/api/budget/"),
            ("Admin page", "/admin/"),
        ],
        "username": request.user
    }

    if sidebar_context["budget_balanced"] is not None:
        messages.warning(
            request,
            f"Warning: Budget imbalanced (value: {sidebar_context['budget_balanced']}, should be 1)",
        )

    return {**context, **sidebar_context}


def verify_user(request):
    """
    :return: None if user is authenticated, returns redirect if they are not authenticated
    """
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse(settings.LOGIN_URL))
    else:
        return None

