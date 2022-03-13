from unittest.mock import patch
from api2.models import Transaction
from cron.jobs.clean_up_predictions import CleanUpPredictions
from cron.tests import CronJobTest

MODULE = "cron.jobs.clean_up_predictions"


class TestCleanUpPredictions(CronJobTest):
    job = CleanUpPredictions

    def test(self):
        budget = self.generate_budget()
        self.generate_transaction(budget, prediction=True, date=self.now)
        self.generate_transaction(budget, prediction=True, date=self.now.shift(days=-1))

        unaffected_trans = [
            self.generate_transaction(
                budget, prediction=False, date=self.now.shift(days=-1)
            ),
            self.generate_transaction(budget, prediction=False, date=self.now),
        ]

        with patch(f"{MODULE}.arrow.now", return_value=self.now):
            self.start()

        trans = Transaction.objects.all()
        self.assertLengthEqual(trans, len(unaffected_trans))
