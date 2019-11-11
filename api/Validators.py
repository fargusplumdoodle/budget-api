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
import datetime


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

    @staticmethod
    def check_parameters(get):
        """
         checks if each parameter is in GET request
        :param get: dict of get parameters
        :raises Validation.ValidationError:
        """
        valid_params = ['start', 'end', 'budgets']
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
        try:
            start_list = [int(x) for x in start.split('-')]
            end_list = [int(x) for x in end.split('-')]

            start = datetime.date(start_list[0], start_list[1], start_list[2])
            end = datetime.date(end_list[0], end_list[1], end_list[2])
        except Exception as e:
            raise ValidationError("invalid start or end date")

        if start < datetime.date(2019, 10, 1) or start > datetime.date(2077, 7, 31):
            raise ValidationError("Start date cannot be less than (2019, 10, 1) or greater than (2077, 7, 31)")
        if end < datetime.date(2019, 10, 1) or end > datetime.date(2077, 7, 31):
            raise ValidationError("End date cannot be less than (2019, 10, 1) or greater than (2077, 7, 31)")

class ValidationError(Exception):
    pass
