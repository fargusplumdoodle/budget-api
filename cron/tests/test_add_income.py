from unittest.mock import patch

from django.contrib.auth.models import User

from cron.jobs.monthly.add_income import AddIncome
from cron.tests import CronJobTest


MODULE = "cron.jobs.monthly.add_income"


class AddIncomeTestCase(CronJobTest):
    job = AddIncome

    def test(self):
        [self.generate_user() for _ in range(5)]

        with patch(f"{MODULE}.add_income") as mock_add_income:
            self.start()

        self.assertEqual(mock_add_income.call_count, User.objects.count())
        for user in User.objects.all():
            mock_add_income.assert_any_call(user)
