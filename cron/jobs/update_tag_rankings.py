import arrow

from api2.models import Tag, Transaction
from cron.cron import CronJob


class UpdateTagRankings(CronJob):
    name = "Update Tag Frequency Rankings"

    def run(self, *args, **kwargs):
        last_6_months = arrow.now().shift(months=-6).datetime

        for tag in Tag.objects.all():
            tag.rank = Transaction.objects.filter(
                tags=tag, date__gte=last_6_months, prediction=False
            ).count()
            tag.save()
