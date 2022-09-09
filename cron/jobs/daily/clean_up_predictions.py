import arrow

from api2.models import Transaction
from cron.cron import CronJob


class CleanUpPredictions(CronJob):
    name = "Remove predictions that are in the past"

    def run(self, *args, **kwargs):
        now = arrow.now()
        Transaction.objects.filter(date__lte=now.datetime, prediction=True).delete()
