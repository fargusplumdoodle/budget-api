from django.db import models


class Budget(models.Model):
    name = models.TextField(max_length=20, unique=True)
    percentage = models.FloatField(max_length=100, null=True)
    initial_balance = models.FloatField(max_length=4000, null=True)
    current_balance = models.FloatField(max_length=4000, null=True)
    monthly_contribution = models.FloatField(max_length=4000, null=True)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    amount = models.FloatField(max_length=4000)
    description = models.TextField(max_length=300, null=True)
    budget = models.ForeignKey(Budget, null=True, on_delete=models.SET_NULL)
    date = models.DateField()

    def __str__(self):
        return str(self.amount) + "_" + str(self.date)


class Config(models.Model):
    paycheque_amount = models.FloatField(max_length=4000)
