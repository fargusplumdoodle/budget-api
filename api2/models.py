import hashlib
from typing import List
import arrow
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum, Q


class Budget(models.Model):
    name = models.CharField(max_length=20)
    percentage = models.IntegerField(default=0)
    initial_balance = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    income_per_month = models.IntegerField(null=True)
    outcome_per_month = models.IntegerField(null=True)
    rank = models.IntegerField(
        default=0, help_text="Notates how frequent this budget is used"
    )

    class Meta:
        unique_together = ("name", "user")
        ordering = ["-rank", "name"]

    def balance(self, date_range=None) -> int:
        # the current balance is equal to the sum of all transactions plus the initial balance
        balance = self.initial_balance
        transactions = Transaction.objects.filter(budget=self, prediction=False)

        if date_range:
            assert isinstance(date_range, Q)
            transactions = transactions.filter(date_range)

        for x in transactions:
            balance += x.amount
        return balance

    def pretty_percentage(self):
        return str(self.percentage)

    def calculate_income_outcome(self, time_period=6, save=False):
        def get_amount_per_month(total):
            if total:
                return round(total / time_period)
            else:
                return 0

        time_period_range = (
            arrow.now().shift(months=0 - time_period).datetime,
            arrow.now().datetime,
        )
        transactions = Transaction.objects.filter(
            date__range=time_period_range, budget=self, prediction=False
        )
        total_income = transactions.filter(income=True).aggregate(Sum("amount"))[
            "amount__sum"
        ]
        total_outcome = transactions.filter(income=False).aggregate(Sum("amount"))[
            "amount__sum"
        ]

        self.income_per_month = get_amount_per_month(total_income)
        self.outcome_per_month = get_amount_per_month(total_outcome)

        if save:
            self.save()

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=30, db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    rank = models.IntegerField(
        default=0, help_text="Notates how frequent this tag has been used"
    )

    class Meta:
        unique_together = ("name", "user")
        ordering = ["-rank", "name"]

    def __str__(self) -> str:
        return f"<Tag: {self.name}>"


class Transaction(models.Model):
    MAX_TRANSACTION_SUPPORTED = 100_000_00  # No greater than 100,000 dollars
    MIN_TRANSACTION_SUPPORTED = -100_000_00  # No less than 100,000 dollars

    amount = models.IntegerField()
    description = models.CharField(max_length=300, blank=True)
    budget = models.ForeignKey(Budget, on_delete=models.SET_NULL, null=True)
    date = models.DateField(db_index=True)

    tags = models.ManyToManyField(Tag, blank=True)

    income = models.BooleanField(
        default=False, help_text="Signifies that this is part of an income"
    )
    transfer = models.BooleanField(
        default=False, help_text="Signifies that this is part of a transfer"
    )
    prediction = models.BooleanField(
        default=False,
        help_text="Signifies this transaction is only an estimate and that it actually does not exist",
    )

    def pretty_amount(self):
        return str(self.amount)

    def __str__(self):
        return f"{self.budget.name}_{self.date}_{self.amount}"


class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    expected_monthly_net_income = models.IntegerField(default=0)

    # Prediction info
    #   Fields:
    income_frequency_days = models.IntegerField(
        default=14, help_text="How many days to expect for each income"
    )
    analyze_start = models.DateField(null=True)
    analyze_end = models.DateField(null=True)
    predict_start = models.DateField(null=True)
    predict_end = models.DateField(null=True)
    #   Metadata:
    currently_calculating_predictions = models.BooleanField(default=False)
    prediction_state_hash = models.BinaryField(
        null=True, max_length=40, help_text="Sha1sum of prediction input fields"
    )

    def calculate_prediction_state_hash(self) -> bytes:
        date_fields = [
            self.analyze_start,
            self.analyze_end,
            self.predict_start,
            self.predict_end,
        ]
        prediction_settings_fields: List[str] = [
            *[str(d) for d in date_fields],
            str(self.income_frequency_days),
            str(self.expected_monthly_net_income),
        ]
        hash = hashlib.sha1()

        for field in prediction_settings_fields:
            hash.update(field.encode())

        return hash.digest()
