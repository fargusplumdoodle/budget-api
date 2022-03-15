import logging
import arrow
from api2.models import Transaction, UserInfo
from cron.cron import CronJob
from reports.predictor import Predictor

logger = logging.getLogger(__name__)


class CreatePredictions(CronJob):
    name = "Create Predictions based on user info"

    def run(self, *args, **kwargs):
        for user_info in UserInfo.objects.all():
            user = user_info.user
            logger.info('Deleting all predictions for "%s"', user.username)
            Transaction.objects.filter(prediction=True, budget__user=user).delete()

            logger.info(
                'Analysing trans for "%s" from "%s" to now',
                user.username,
                user_info.analyze_start,
            )
            user_info.currently_calculating_predictions = True
            user_info.save()

            analyze_range = (
                arrow.get(user_info.analyze_start),
                arrow.now(),
            )
            predict_range = (
                arrow.now().shift(days=1),
                arrow.get(user_info.predict_end),
            )

            predictor = Predictor(user, analyze_range, predict_range)
            created_predictions = predictor.run()

            logger.info(
                'Created "%s" predicted transactions for "%s" until "%s"',
                created_predictions.count(),
                user.username,
                user_info.predict_end,
            )
