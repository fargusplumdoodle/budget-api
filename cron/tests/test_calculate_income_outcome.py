from cron.jobs.daily.calculate_income_outcome import CalculateIncomeOutcome
from cron.tests import CronJobTest


class TestCalculateIncomeOutcome(CronJobTest):
    job = CalculateIncomeOutcome

    def test_called(self):
        budget = self.generate_budget()
        self.generate_transaction(budget, amount=-3000, income=False)
        self.generate_transaction(budget, amount=3000, income=True)

        self.start()

        budget.refresh_from_db()
        self.assertEqual(budget.income_per_month, 1000)
        self.assertEqual(budget.outcome_per_month, -1000)
