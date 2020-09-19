from django.contrib.auth.models import User
from django.db import models


class Budget(models.Model):
    name = models.CharField(max_length=20, unique=True)
    percentage = models.IntegerField(default=0)
    initial_balance = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def balance(self):
        # the current balance is equal to the sum of all transactions plus the initial balance
        balance = self.initial_balance
        for x in Transaction.objects.filter(budget=self):
            balance += x.amount
        return balance

    def pretty_percentage(self):
        return str(self.percentage)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    amount = models.IntegerField()
    description = models.CharField(max_length=300)
    budget = models.ForeignKey(Budget, on_delete=models.SET_NULL, null=True)
    date = models.DateField()

    MAX_TRANSACTION_SUPPORTED = 100_000_00  # No greater than 10,000 dollars
    MIN_TRANSACTION_SUPPORTED = -100_000_00  # No greater than 10,000 dollars

    def pretty_amount(self):
        return str(self.amount)

    def __str__(self):
        return f"{self.budget.name}_{self.date}_{self.amount}"
