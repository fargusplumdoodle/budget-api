import abc
from typing import Optional, Type

from django.db.migrations import RunPython
from django.db.migrations.state import StateApps
from django.db.models import Model


class CustomMigration(abc.ABC):
    """
    For writing custom Django tests that are also testable

    Examples:
         grep -rn CustomMigration

    Writing custom migration classes:
        - Whenever you make a query you must include the `.using(self.db)` function in your query
        - Whenever you want to reference a model you must use the `self.get_model()` function
          to retrieve the class
        - Include your CustomMigration in the Migration by adding the CustomMigration.get_operation()
          function to your Migration.operations (see examples)
        - Overwrite both `forward()` and `backward()` functions
        - Do not reference custom functions on your models, if they change in the future it could break the migration
        - Do not reference code outside of the tests file
        - DO NOT CHANGE MIGRATIONS AFTER THEY HAVE BEEN DEPLOYED

    Remember:
        Whatever your migration is, it will be ran **before** your tests
    """

    def __init__(self, app: Optional[StateApps], db: str, testing: bool = False):
        self.app = app
        self.db = db
        self.testing = testing

    def get_model(self, app_label: str, model_name: str) -> Type[Model]:
        """
        Allows custom tests to get models from both a test environment
        as well as when the tests are being ran
        """
        if self.testing:
            models = __import__(f"{app_label}.models", fromlist=[model_name])
            return getattr(models, model_name)
        else:
            assert self.app
            return self.app.get_model(app_label, model_name)

    @abc.abstractmethod
    def forward(self):
        raise NotImplementedError

    @abc.abstractmethod
    def reverse(self):
        raise NotImplementedError

    @classmethod
    def get_operation(cls, elidable=True) -> RunPython:
        def run_forward(apps, schema_editor):
            cls(apps, schema_editor.connection.alias).forward()

        def run_reverse(apps, schema_editor):
            cls(apps, schema_editor.connection.alias).reverse()

        return RunPython(run_forward, run_reverse, elidable=elidable)
