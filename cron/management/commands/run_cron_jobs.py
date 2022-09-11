from django.core.management.base import BaseCommand, CommandError

from cron.cron import CronJobRunner


class Command(BaseCommand):
    help = """
    Runs cron jobs
    """

    def add_arguments(self, parser):
        parser.add_argument("batch", type=str)

    def handle(self, *args, **options):
        if options.get("batch") not in CronJobRunner.batch_map:
            raise CommandError(
                f"Invalid batch option, can be {[*CronJobRunner.batch_map.keys()]}"
            )

        CronJobRunner.execute_jobs(batch=options["batch"])
