# Generated by Django 4.0.1 on 2022-09-08 14:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("api2", "0016_tag_common_budget_tag_common_transaction_amount"),
    ]

    operations = [
        migrations.AddField(
            model_name="budget",
            name="parent",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="api2.budget",
            ),
        ),
    ]
