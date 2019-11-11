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
        return Response(str(e), status=400, content_type="text/plain")

Each class will have a "validate" function that will call other functions in the class
this makes testing easy

If any issue occurs, we raise a ValidationError("description of issue"). ValidationError
is defined in this file
"""


class GraphBudgetHistory:
    """
    GET Parameters:
        - start date
        - end date
        - budgets list

    Procedure
           - check if parameters are in request
           - check if dates are valid
           - check if budgets actually exist

    """

    @staticmethod
    def validate(request):
        raise ValidationError("invalid x")


class ValidationError(Exception):
    pass
