import arrow
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum


class Budget(models.Model):
    name = models.CharField(max_length=20)
    percentage = models.IntegerField(default=0)
    initial_balance = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    income_per_month = models.IntegerField(null=True)
    outcome_per_month = models.IntegerField(null=True)

    class Meta:
        unique_together = ("name", "user")

    def balance(self):
        # the current balance is equal to the sum of all transactions plus the initial balance
        balance = self.initial_balance
        for x in Transaction.objects.filter(budget=self):
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
            date__range=time_period_range, budget=self
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

    class Meta:
        unique_together = ("name", "user")


class Transaction(models.Model):
    MAX_TRANSACTION_SUPPORTED = 100_000_00  # No greater than 100,000 dollars
    MIN_TRANSACTION_SUPPORTED = -100_000_00  # No less than 100,000 dollars

    amount = models.IntegerField()
    description = models.CharField(max_length=300)
    budget = models.ForeignKey(Budget, on_delete=models.SET_NULL, null=True)
    date = models.DateField(db_index=True)

    tags = models.ManyToManyField(Tag, blank=True)

    income = models.BooleanField(
        default=False, help_text="Signifies that this is part of an income"
    )
    transfer = models.BooleanField(
        default=False, help_text="Signifies that this is part of a transfer"
    )

    def pretty_amount(self):
        return str(self.amount)

    def __str__(self):
        return f"{self.budget.name}_{self.date}_{self.amount}"
