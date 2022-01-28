from django.urls import include

from budget.utils.test import BudgetTestCase
from budget.utils.urls import Path


class TestPath(BudgetTestCase):
    def test(self):
        p = Path("v2", include("api2.urls"))
        paths = {str(path.pattern) for path in [*p]}
        expected_paths = {"v2", "api/v2"}
        self.assertEqual(paths, expected_paths)
