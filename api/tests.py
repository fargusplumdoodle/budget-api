from django.test import TestCase
from django.core.management import call_command
from .management.commands.load_transactions import Command as LoadTransaction


class load_transaction(TestCase):

    def test_validate_csv(self):
        lt = LoadTransaction()

        # trying valid input
        fields = [x for x in lt.REQUIRED_FIELDS]
        assert lt.invalid_csv_headers(fields) is None

        # trying one less field
        fields.pop()
        assert lt.invalid_csv_headers(fields) is not None


