from django.db import models
from django.contrib.auth.models import User


class Budget(models.Model):
    name = models.TextField(max_length=20, unique=True)
    percentage = models.FloatField(max_length=100)
    initial_balance = models.FloatField(max_length=4000, null=True)

    def balance(self):
        # the current balance is equal to the sum of all transactions plus the inital balance
        balance = self.initial_balance
        for x in Transaction.objects.filter(budget=self):
            balance += x.amount
        return "%.2f" % balance

    def pretty_percentage(self):
        return "%.2f" % self.percentage

    def __str__(self):
        return self.name


class Transaction(models.Model):
    amount = models.FloatField(max_length=4000)
    description = models.TextField(max_length=300, null=True)
    budget = models.ForeignKey(Budget, null=True, on_delete=models.SET_NULL)
    date = models.DateField()

    def pretty_amount(self):
        return "%.2f" % self.amount

    def __str__(self):
        return str(self.amount) + "_" + str(self.date)


class Profile(models.Model):
    """
    For keeping track of basic user information
    ------------------------------------------

    if there are two or more budgets to a single user, only the first one
    will be used
        Profile.objects.filter(user=user).first()
    """
    # the amount each paycheck is, assuming they get paid every 14 days
    pay_biweekly = models.IntegerField()

    # this is for determining which days you are paid for
    # just give any day that you had a paycheque.
    # this program can calculate every other paycheque
    # you have ever had by adding/subtracting 14 days
    initial_paydate = models.DateField()

    # for associating a user with their profile
    user = models.ForeignKey(User, on_delete=models.CASCADE)
