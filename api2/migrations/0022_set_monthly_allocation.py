# Generated by Django 4.0.1 on 2022-09-09 01:50

from django.db import migrations

from api2.custom_migrations.budget_tree.SetMonthlyAllocation import SetMonthlyAllocation


class Migration(migrations.Migration):

    dependencies = [
        ("api2", "0021_budget_monthly_allocation"),
    ]

    operations = [SetMonthlyAllocation.get_operation()]
