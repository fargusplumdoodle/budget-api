from django.apps import AppConfig


class Api2Config(AppConfig):
    name = "api2"

    def ready(self):
        from . import signals  # noqa: F401
