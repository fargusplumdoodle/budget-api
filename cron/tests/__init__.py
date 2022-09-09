import abc
from typing import Type
from unittest.mock import patch

from budget.utils.test import BudgetTestCase
from cron.cron import CronJob, CronJobRunner


class CronJobTest(BudgetTestCase, abc.ABC):
    job: Type[CronJob]

    def start(self):
        jobs = [self.job()]
        with patch("cron.cron.CronJobRunner._discover_jobs", return_value=jobs):
            CronJobRunner.execute_cron_daily_jobs()
