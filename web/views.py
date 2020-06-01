from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Budget, Transaction
from .helper import budgets_sum_to_one, add_money as add_money_function
from .forms import AddMoneyForm, GraphHistoryForm, AddTransactionForm
from budget import settings
from .Graph import Graph
import datetime
from . import Validators


class GraphBudgetHistory(APIView):
    def get(self, request, format=None):
        # x will be a redirect to the login page if the user is not authenticated
        x = verify_user(request)
        if x:
            return x

        try:
            Validators.GraphBudgetHistory.validate(request)
        except Validators.ValidationError as e:
            return Response(
                {"error": str(e)}, status=400, content_type="application/json"
            )

        try:
            budgets = Budget.objects.filter(
                name__in=request.GET.get("budgets", "no budgets yo").split(",")
            )

            start_list = [int(x) for x in request.GET.get("start", "").split("-")]
            end_list = [int(x) for x in request.GET.get("end", "").split("-")]

            start = datetime.date(start_list[0], start_list[1], start_list[2])
            end = datetime.date(end_list[0], end_list[1], end_list[2])

            response = Graph.balance_history(budgets, start, end)
        except Exception:
            return Response(
                "unknown error occurred", status=400, content_type="text/plain"
            )

        return Response(response, status=200, content_type="application/json")


def dashboard(request):
    # x will be a redirect to the login page if the user is not authenticated
    x = verify_user(request)
    if x:
        return x

    context = {}

    context["budget_list"] = Budget.objects.all()
    context["budget_balanced"] = budgets_sum_to_one()

    context["total_money"] = "%.2f" % float(
        sum([x.amount for x in Transaction.objects.all()])
        + sum([x.initial_balance for x in context["budget_list"]])
    )

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


def add_transaction(request):
    # x will be a redirect to the login page if the user is not authenticated
    x = verify_user(request)
    if x:
        return x
    # adding form to context
    context = {"add_transaction_form": AddTransactionForm}

    if request.method == "POST":
        form = AddTransactionForm(request.POST)

        if form.is_valid():
            # attempting to add amount
            try:
                # Creating transaction
                trans = Transaction.objects.create(
                    amount=form.cleaned_data.get("amount"),
                    description=form.cleaned_data.get("description"),
                    budget=Budget.objects.get(name=form.cleaned_data.get("budget")),
                    date=form.cleaned_data.get("date"),
                )
                messages.success(
                    request, f'Added {trans.amount}$ to {trans.budget.name}!'
                )
                # if ANYTHING went wrong here, let them know
            except AssertionError:
                messages.warning(
                    request,
                    f'Failed to add {form.cleaned_data.get("amount")}, budget imbalanced. Balance your budget first',
                )
        else:
            messages.warning(request, f"Invalid input")

        return render(
            request, "api/add_transaction.html", context=add_sidebar_context(context, request)
        )
    else:
        # returning a regular page
        return render(
            request, "api/add_transaction.html", context=add_sidebar_context(context, request)
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
                transactions = add_money_function(form.cleaned_data.get("amount"), save=True)

                # adding trans list to show to the user
                context["trans_list"] = transactions

                messages.success(
                    request, f'Added {form.cleaned_data.get("amount")}$ to budgets!'
                )
                # if ANYTHING went wrong here, let them know
            except AssertionError:
                messages.warning(
                    request,
                    f'Failed to add {form.cleaned_data.get("amount")}, budget imbalanced. Balance your budget first',
                )
            # except:
            #    messages.warning(
            #        request, f'Failed to add {form.cleaned_data.get("amount")}'
            #    )
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
            ("Add transaction", "/add_transaction/"),
            ("View Budgets", "/admin/web/budget/"),
            ("Admin page", "/admin/"),
        ],
        "username": request.user,
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


def graph_history_page(request):
    """
    For generating graphs
    This page does not use the sidebar
    """

    x = verify_user(request)
    if x:
        return x

    context = {
        "graph_history_form": GraphHistoryForm,
        "budgets": [x.name for x in Budget.objects.all()],
    }

    return render(request, "api/graph/graph_history.html", context=context)
