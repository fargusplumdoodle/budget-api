from unittest.mock import patch
from cron.jobs.create_predictions import CreatePredictions
from cron.tests import CronJobTest

MODULE = "cron.jobs.create_predictions"
PREDICTIONS_MODULE = "reports.predictor.Predictor"


class TestCreatePredictions(CronJobTest):
    job = CreatePredictions

    def test_needs_predictions_created(self):
        user = self.generate_user()
        user_info = self.generate_user_info(
            user=user, prediction_state_hash="".encode()
        )
        self.assertTrue(self.job()._needs_predictions_created(user_info))

        user_info.prediction_state_hash = user_info.calculate_prediction_state_hash()

        self.assertFalse(self.job()._needs_predictions_created(user_info))

    def test_start(self):
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
