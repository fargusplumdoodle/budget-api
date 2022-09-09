import abc
from importlib import import_module

import logging

from os import listdir
from os.path import dirname, basename
from typing import List
import re

import arrow
from .jobs import daily, monthly

logger = logging.getLogger(__name__)


class CronJob(abc.ABC):
    """
    Override to run cron daily
    """

    name: str
    skip: bool = False

    def start(self, *args, **kwargs):
        self.run(*args, **kwargs)

    def run(self, *args, **kwargs):
        raise NotImplementedError()


class CronJobRunner:
    _extension = re.compile(r"\.py$")

    @classmethod
    def _discover_jobs(cls, mod) -> List[CronJob]:
        cron_jobs: List[CronJob] = []
        for filename in listdir(dirname(mod.__file__)):
            module_name = re.sub(cls._extension, "", basename(filename))
            if module_name == "__init__":
                continue
            module = import_module(f"cron.jobs.daily.{module_name}")
            for entry in dir(module):
                job = getattr(module, entry)
                try:
                    if issubclass(job, CronJob) and not job.skip and not job == CronJob:
                        cron_jobs.append(job())
                except TypeError:
                    pass
        return cron_jobs

    @classmethod
    def execute_jobs(cls, mod):
        for job in cls._discover_jobs(mod):
            logger.info("%s STARTING: %s", arrow.now().isoformat(), job.name)
            job.start()
            logger.info("%s COMPLETE: %s", arrow.now().isoformat(), job.name)

    @classmethod
    def execute_cron_daily_jobs(cls):
        cls.execute_jobs(daily)

    @classmethod
    def execute_cron_monthly_jobs(cls):
        cls.execute_jobs(monthly)
