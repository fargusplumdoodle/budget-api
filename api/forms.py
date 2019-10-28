from django import forms


class AddMoneyForm(forms.Form):
    amount = forms.IntegerField(
        required=True,
    )
