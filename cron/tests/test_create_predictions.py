from unittest.mock import patch

from django.contrib.auth.models import User

from api2.models import Transaction, UserInfo
from cron.jobs.daily.create_predictions import CreatePredictions
from cron.tests import CronJobTest

MODULE = "cron.jobs.daily.create_predictions"
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

    def test_start_no_user_info(self):
        User.objects.all().delete()
        UserInfo.objects.all().delete()

        user= self.generate_user()
        user_info = self.generate_user_info(user=user )
        user_info.analyze_start=None
        user_info.save()

        self.start()

        self.assertEqual(
            Transaction.objects.filter(prediction=True).count(), 0
        )




