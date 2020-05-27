from django import forms
from .models import Budget
import datetime


class AddMoneyForm(forms.Form):
    amount = forms.FloatField(required=True)


class GraphHistoryForm(forms.Form):
    start = forms.DateField(
        required=True,
        initial=datetime.date.today,
    )
    end = forms.DateField(
        required=True,
        initial=datetime.date.today,
    )
    budgets = forms.ModelMultipleChoiceField(queryset=Budget.objects.all(), required=True)

    def clean_start(self):
        # ensuring date is within range in documentation
        if datetime.datetime(self.start) < datetime.date(2019, 10, 1):
            raise self.ValidationError("Date must be between 2019-10-01 and 2077-07-31 ")
        if datetime.datetime(self.start) > datetime.date(2077, 7, 31):
            raise self.ValidationError("Date must be between 2019-10-01 and 2077-07-31 ")

    def clean_end(self):
        # ensuring date is within range in documentation
        if datetime.datetime(self.end) < datetime.date(2019, 10, 1):
            raise self.ValidationError("Date must be between 2019-10-01 and 2077-07-31 ")
        if datetime.datetime(self.end) > datetime.date(2077, 7, 31):
            raise self.ValidationError("Date must be between 2019-10-01 and 2077-07-31 ")
