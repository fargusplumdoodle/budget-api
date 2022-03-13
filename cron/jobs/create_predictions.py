import logging
import arrow
from api2.models import UserInfo
from cron.cron import CronJob
from reports.predictor import Predictor

logger = logging.getLogger(__name__)


class CreatePredictions(CronJob):
    name = "Create Predictions based on user info"

    def run(self, *args, **kwargs):
        for user_info in UserInfo.objects.all():
            user = user_info.user

            if not self._needs_predictions_created(user_info):
                logger.info(
                    'User "%s" does not need predictions created', user.username
                )
                continue

            logger.info(
                'Analysing trans for "%s" in range (%s, %s)',
                user.username,
                user_info.analyze_start,
                user_info.analyze_end,
            )
            user_info.currently_calculating_predictions = True
            user_info.save()

            analyze_range = (
                arrow.get(user_info.analyze_start),
                arrow.get(user_info.analyze_end),
            )
            predict_range = (
                arrow.get(user_info.predict_start),
                arrow.get(user_info.predict_end),
            )

            predictor = Predictor(user, analyze_range, predict_range)
            created_predictions = predictor.run()

            logger.info(
                'Created "%s" predicted transactions for "%s" in range (%s, %s)',
                created_predictions.count(),
                user.username,
                user_info.analyze_start,
                user_info.analyze_end,
            )
            user_info.prediction_state_hash = (
                user_info.calculate_prediction_state_hash()
            )
            user_info.currently_calculating_predictions = False
            user_info.save()

    def _needs_predictions_created(self, user_info: UserInfo) -> bool:
        return (
            user_info.calculate_prediction_state_hash()
            != user_info.prediction_state_hash
        )
