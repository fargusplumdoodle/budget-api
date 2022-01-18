from cron.jobs.update_budget_rankings import UpdateBudgetRankings
from cron.tests import CronJobTest


class UpdateBudgetRankingsTest(CronJobTest):
    job = UpdateBudgetRankings

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.budget = cls.generate_budget()

    def test(self):
        budget_with_rank = self.generate_budget(rank=0)
        budget_without_rank = self.generate_budget(rank=0)

        self.generate_transaction(
            budget_without_rank,
            date=self.now.shift(months=-6, days=-1),
        )

        for _ in range(10):
            self.generate_transaction(budget_with_rank, date=self.now)

        self.start()

        budget_with_rank.refresh_from_db()
        budget_without_rank.refresh_from_db()
        self.assertEqual(budget_with_rank.rank, 10)
        self.assertEqual(budget_without_rank.rank, 0)
