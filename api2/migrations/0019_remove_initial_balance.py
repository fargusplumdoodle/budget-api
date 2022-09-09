from django.db import migrations, models

from api2.custom_migrations.budget_tree.RemoveInitialBalance import RemoveInitialBalance


class Migration(migrations.Migration):

    dependencies = [
        ("api2", "0018_budget_tree"),
    ]

    operations = [
        RemoveInitialBalance.get_operation()
    ]
