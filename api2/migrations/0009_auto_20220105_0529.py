# Generated by Django 3.2.10 on 2022-01-05 05:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api2", "0008_auto_20211225_0509"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="tag",
            options={"ordering": ["-rank", "name"]},
        ),
        migrations.AddField(
            model_name="tag",
            name="rank",
            field=models.IntegerField(
                default=0, help_text="Notates how frequent this tag has been used"
            ),
        ),
    ]