from django.core.management.base import BaseCommand

from cron.cron import CronJobRunner


class Command(BaseCommand):
    help = """
    Runs cron jobs
    """

    def handle(self, *args, **options):
        CronJobRunner.execute_cron_jobs()
