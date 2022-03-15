from unittest.mock import patch

from api2.models import Transaction
from cron.jobs.create_predictions import CreatePredictions
from cron.tests import CronJobTest

MODULE = "cron.jobs.create_predictions"
PREDICTIONS_MODULE = "reports.predictor.Predictor"


class TestCreatePredictions(CronJobTest):
    job = CreatePredictions

    def setUp(self) -> None:
        super().setUp()
        self.budget = self.generate_budget()

    def test_start(self):
        existing_prediction = self.generate_transaction(self.budget, prediction=True)
        with (
            patch(f"{MODULE}.arrow.now", return_value=self.now),
            patch(
                f"{PREDICTIONS_MODULE}._generate_transactions", return_value=[]
            ) as mock_generate_trans,
            patch(
                f"{PREDICTIONS_MODULE}._generate_income_transactions", return_value=[]
            ) as mock_generate_income,
        ):
            self.start()
        mock_generate_trans.assert_called_once()
        mock_generate_income.assert_called_once()

        with self.assertRaises(Transaction.DoesNotExist):
            existing_prediction.refresh_from_db()
