from cron.jobs.update_tag_rankings import UpdateTagRankings
from cron.tests import CronJobTest


class UpdateTagRankingsTest(CronJobTest):
    job = UpdateTagRankings

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.budget = cls.generate_budget()

    def test(self):
        tag_with_rank = self.generate_tag(rank=0)
        tag_without_rank = self.generate_tag(rank=0)

        self.generate_transaction(
            self.budget,
            tags=[tag_without_rank],
            date=self.now.shift(months=-6, days=-1),
        )

        for _ in range(10):
            self.generate_transaction(self.budget, tags=[tag_with_rank], date=self.now)

        self.start()

        tag_with_rank.refresh_from_db()
        tag_without_rank.refresh_from_db()
        self.assertEqual(tag_with_rank.rank, 10)
        self.assertEqual(tag_without_rank.rank, 0)
