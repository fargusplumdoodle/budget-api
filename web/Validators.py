"""
VALIDATORS
----------

This file contains a series of Classes for each thing that needs to be validated
in this application.

For example, if you wanted to validate the GraphBudgetHistory endpoint you would use
something like this in your endpoint

    from . import Validators
    try:
        Validators.GraphBudgetHistory.validate(request)
    except Validators.ValidationError as e:
            return Response(
                {"error": str(e)}, status=400, content_type="application/json"
            )

Each class will have a "validate" function that will call other functions in the class
this makes testing easy

If any issue occurs, we raise a ValidationError("description of issue"). ValidationError
is defined in this file
"""
import datetime
from api.models import Budget


class GraphBudgetHistory:
    """
    GET Parameters:
        - start date
        - end date
        - budgets list

    Procedure
           - check if parameters are in request
           - check if dates are valid
                - if they are proper dates
                - if they are in specified range
           - check if budgets actually exist

    """

    @staticmethod
    def validate(request):
        # - check if parameter are in request
        GraphBudgetHistory.check_parameters(request.GET)

        # - check if dates are valid
        GraphBudgetHistory.check_dates(request.GET.get("start"), request.GET.get("end"))

        # - test if budgets actually exist
        GraphBudgetHistory.check_budgets(request.GET.get("budgets"))

    @staticmethod
    def check_parameters(get):
        """
         checks if each parameter is in GET request
        :param get: dict of get parameters
        :raises Validation.ValidationError:
        """
        valid_params = ["start", "end", "budgets"]
        for param in valid_params:
            if param not in get:
                raise ValidationError(f"Error: Missing {param} from get parameters")

    @staticmethod
    def check_dates(start, end):
        """
           - check if dates are valid
                - if they are proper dates
                - if they are in specified range
        :param start: str start date
        :param end: str end date
        :raises Validation.ValidationError:
        """
        dates = [start, end]
        for date in dates:
            try:
                ls = [int(x) for x in date.split("-")]
                tested_date = datetime.date(ls[0], ls[1], ls[2])
            except Exception as e:
                raise ValidationError("invalid start or end date")

            if tested_date < datetime.date(2019, 10, 1) or tested_date > datetime.date(
                2077, 7, 31
            ):
                raise ValidationError(
                    "start and end dates cannot be less than (2019, 10, 1) or greater than (2077, 7, 31)"
                )

    @staticmethod
    def check_budgets(budgets):
        """
        Checks if budgets parameter is valid and that all budgets exist
        :param budgets: string list of budgets. Example: food,housing,personal
        :return:
        """
        if not isinstance(budgets, str):
            raise ValidationError(
                'Error, invalid list of budgets. Example: "food,housing,personal"'
            )

        try:
            budgets_ls = budgets.split(",")
        except:
            raise ValidationError(
                'Error, invalid list of budgets. Example: "food,housing,personal"'
            )

        if len(budgets_ls) < 1:
            raise ValidationError(
                'Error, No budgets supplied. invalid list of budgets. Example: "food,housing,personal"'
            )

        actual_budgets = [x.name for x in Budget.objects.all()]
        for budget in budgets_ls:
            if budget not in actual_budgets:
                raise ValidationError(
                    f'Error, budget {budget} does not exist. Example: "food,housing,personal"'
                )


class ValidationError(Exception):
    pass
