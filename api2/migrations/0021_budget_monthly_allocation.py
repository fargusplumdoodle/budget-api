# Generated by Django 4.0.1 on 2022-09-09 01:50

from django.db import migrations, models

from api2.custom_migrations.budget_tree.SetMonthlyAllocation import SetMonthlyAllocation


class Migration(migrations.Migration):

    dependencies = [
        ('api2', '0020_remove_budget_initial_balance'),
    ]

    operations = [
        migrations.AddField(
            model_name='budget',
            name='monthly_allocation',
            field=models.IntegerField(default=0),
        ),
    ]
