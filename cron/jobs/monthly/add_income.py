import arrow
from django.contrib.auth.models import User

from api2.utils.add_income import add_income
from cron.cron import CronJob


class AddIncome(CronJob):

    name = "Income"

    # Creates an income transaction for each user

    def run(self, *args, **options):
        for user in User.objects.all():
            add_income(user)
