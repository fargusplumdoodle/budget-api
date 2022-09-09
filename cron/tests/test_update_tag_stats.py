from cron.jobs.daily import UpdateTagStats
from cron.tests import CronJobTest


class UpdateTagRankingsTest(CronJobTest):
    job = UpdateTagStats

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.budget = cls.generate_budget()

    def setUp(self) -> None:
        self.tag = self.generate_tag()

    def test_rank(self):
        tag_without_rank = self.generate_tag(rank=0)

        self.generate_transaction(
            self.budget,
            tags=[tag_without_rank],
            date=self.now.shift(months=-6, days=-1),
        )

        for _ in range(10):
            self.generate_transaction(self.budget, tags=[self.tag], date=self.now)

        self.start()

        self.tag.refresh_from_db()
        tag_without_rank.refresh_from_db()
        self.assertEqual(self.tag.rank, 10)
        self.assertEqual(tag_without_rank.rank, 0)

    def test_common_budget(self):
        second_most_common_budget = self.generate_budget()
        third_most_common_budget = self.generate_budget()

        for _ in range(3):
            self.generate_transaction(self.budget, tags=[self.tag], date=self.now)
        for _ in range(2):
            self.generate_transaction(
                second_most_common_budget, tags=[self.tag], date=self.now
            )
        self.generate_transaction(
            third_most_common_budget, tags=[self.tag], date=self.now
        )

        self.start()
        self.tag.refresh_from_db()
        self.assertEqual(self.tag.common_budget, self.budget)

    def test_common_amount(self):
        most_common_amount = -360
        for _ in range(3):
            self.generate_transaction(
                self.budget, tags=[self.tag], date=self.now, amount=most_common_amount
            )
        for _ in range(2):
            self.generate_transaction(
                self.budget, tags=[self.tag], date=self.now, amount=-145
            )
        self.generate_transaction(
            self.budget, tags=[self.tag], date=self.now, amount=35
        )

        self.start()
        self.tag.refresh_from_db()
        self.assertEqual(self.tag.common_transaction_amount, most_common_amount)
