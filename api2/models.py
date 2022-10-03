import hashlib
import arrow
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum, Q


class Budget(models.Model):
    name = models.CharField(max_length=20)
    monthly_allocation = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    income_per_month = models.IntegerField(null=True)
    outcome_per_month = models.IntegerField(null=True)
    rank = models.IntegerField(
        default=0, help_text="Notates how frequent this budget is used"
    )

    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True)
    is_node = models.BooleanField(default=False)

    class Meta:
        unique_together = ("name", "user")
        ordering = ["-rank", "name"]

    def balance(self, date_range=None) -> int:
        # the current balance is equal to the sum of all transactions plus the initial balance
        balance = 0
        transactions = Transaction.objects.filter(budget=self, prediction=False)
        children = Budget.objects.filter(parent=self)

        if date_range:
            assert isinstance(date_range, Q)
            transactions = transactions.filter(date_range)

        for trans in transactions:
            balance += trans.amount

        for child in children:
            balance += child.balance()

        return balance

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

    # Stats
    rank = models.IntegerField(
        default=0, help_text="Notates how frequent this tag has been used"
    )
    common_transaction_amount = models.IntegerField(null=True)
    common_budget = models.ForeignKey(Budget, on_delete=models.SET_NULL, null=True)

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

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now_add=True)

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
    theme = models.CharField(max_length=20, default="CLASSIC")
    darkMode = models.BooleanField(default=False)

    # Prediction info
    income_frequency_days = models.IntegerField(
        default=14, help_text="How many days to expect for each income"
    )
    analyze_start = models.DateField(
        null=True, help_text="Date to start analyzing transaction behaviour from"
    )
    predict_end = models.DateField(
        null=True, help_text="Date to stop predicting transactions for"
    )

    def calculate_prediction_state_hash(self) -> bytes:
        prediction_settings_fields = [
            self.analyze_start,
            self.predict_end,
            self.income_frequency_days,
            self.expected_monthly_net_income,
        ]
        hash = hashlib.sha1()

        for field in prediction_settings_fields:
            hash.update(str(field).encode())

        return hash.digest()
