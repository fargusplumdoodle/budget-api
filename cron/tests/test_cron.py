from unittest.mock import patch, MagicMock

from budget.utils.test import BudgetTestCase
from cron.cron import CronJobRunner
from cron.management.commands.run_cron_jobs import Command as RunCronJobCommand


class Test(BudgetTestCase):
    def test_command(self):
        with patch(
            "cron.management.commands.run_cron_jobs.CronJobRunner"
        ) as mock_runner:
            RunCronJobCommand().handle()
        mock_runner.execute_cron_jobs.assert_called_once()

    def test_execute_cron_jobs(self):
        jobs = [MagicMock(), MagicMock()]
        with patch("cron.cron.CronJobRunner._discover_jobs", return_value=jobs):
            CronJobRunner.execute_cron_jobs()

        for job in jobs:
            job.start.assert_called_once()
