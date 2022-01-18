# Generated by Django 3.2.10 on 2022-01-18 03:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api2", "0010_alter_transaction_description"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="budget",
            options={"ordering": ["-rank", "name"]},
        ),
        migrations.AddField(
            model_name="budget",
            name="rank",
            field=models.IntegerField(
                default=0, help_text="Notates how frequent this budget is used"
            ),
        ),
    ]