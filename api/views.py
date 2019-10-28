# from rest_framework.response import Response
# from rest_framework.views import APIView
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from .models import Budget, Transaction
from .helper import budgets_sum_to_one, add_money as add_money_function
from .forms import AddMoneyForm


def dashboard(request):
    context = {}

    context["budget_list"] = Budget.objects.all()
    context["budget_balanced"] = budgets_sum_to_one()

    context["trans_list"] = Transaction.objects.order_by("date")[::-1][:10]

    return render(
        request, "api/index.html", context=add_sidebar_context(context, request)
    )


def budget(request, budget_name):
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
    """
    Takes your current context and adds the sidebar information to it
    :param context: current context info for page
    :return: context with sidebar information and your existing info
    """
    sidebar_context = {
        "budget_balanced": budgets_sum_to_one(),
        "sidebar": [
            ("Add transaction", "/admin/api/transaction/add/"),
            ("Admin page", "/admin/"),
        ],
    }

    if sidebar_context["budget_balanced"] is not None:
        messages.warning(
            request,
            f"Warning: Budget imbalanced (value: {sidebar_context['budget_balanced']}, should be 1)",
        )

    return {**context, **sidebar_context}
