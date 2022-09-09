from unittest.mock import patch, MagicMock

from django.core.management import CommandError

from budget.utils.test import BudgetTestCase
from cron.cron import CronJobRunner
from cron.management.commands.run_cron_jobs import Command as RunCronJobCommand


class Test(BudgetTestCase):
    def test_invalid_batch_value(self):
        with self.assertRaises(CommandError):
            RunCronJobCommand().handle(batch="invalid")

        with self.assertRaises(CommandError):
            # Missing batch argument
            RunCronJobCommand().handle()

    def test_daily_command(self):
        batch = "daily"
        with patch(
            "cron.management.commands.run_cron_jobs.CronJobRunner._discover_jobs"
        ) as mock_discover_jobs:
            RunCronJobCommand().handle(batch=batch)

        mock_discover_jobs.assert_called_once_with(
            batch, CronJobRunner.batch_map[batch]
        )

    def test_monthly_command(self):
        batch = "monthly"
        with patch(
            "cron.management.commands.run_cron_jobs.CronJobRunner._discover_jobs"
        ) as mock_discover_jobs:
            RunCronJobCommand().handle(batch=batch)

        mock_discover_jobs.assert_called_once_with(
            batch, CronJobRunner.batch_map[batch]
        )

    def test_execute_cron_jobs(self):
        jobs = [MagicMock(), MagicMock()]
        with patch("cron.cron.CronJobRunner._discover_jobs", return_value=jobs):
            CronJobRunner.execute_jobs()

        for job in jobs:
            job.start.assert_called_once()
