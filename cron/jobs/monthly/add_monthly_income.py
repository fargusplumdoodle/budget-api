from django.contrib.auth.models import User

from api2.utils.add_monthly_income import add_monthly_income
from cron.cron import CronJob


class AddMonthlyIncome(CronJob):

    name = "Add Monthly Income"

    # Creates an income transaction for each user

    def run(self, *args, **options):
        for user in User.objects.all():
            add_monthly_income(user)
