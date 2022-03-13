import arrow
from api2.models import Budget, Tag, Transaction
from budget.utils.test import BudgetTestCase
from reports.predictor import Predictor


class TestPredictor(BudgetTestCase):
    analyze_end_date: arrow.Arrow
    analyze_start_date: arrow.Arrow
    predict_start_date: arrow.Arrow
    predict_end_date: arrow.Arrow

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.housing = cls.generate_budget(name="housing")
        cls.doritos = cls.generate_budget(name="doritos")
        cls.food = cls.generate_budget(name="food")

        cls.tag_rent = cls.generate_tag(name="rent")
        cls.tag_cool_ranch = cls.generate_tag(name="cool ranch")
        cls.tag_groceries = cls.generate_tag(name="groceries")

        cls.analyze_start_date = arrow.get(2022, 1, 1)
        cls.analyze_end_date = arrow.get(2022, 1, 7)

        cls.predict_start_date = arrow.get(2022, 1, 8)
        cls.predict_end_date = arrow.get(2022, 1, 15)

        cls.generate_transaction(
            cls.housing, amount=-100, date=cls.analyze_start_date, tags=[cls.tag_rent]
        )
        cls.generate_transaction(
            cls.doritos,
            amount=-100,
            date=cls.analyze_start_date.shift(days=1),
            tags=[cls.tag_cool_ranch],
        )
        cls.generate_transaction(
            cls.food,
            amount=-50,
            date=cls.analyze_start_date.shift(days=2),
            tags=[cls.tag_groceries],
        )
        cls.generate_transaction(
            cls.food, amount=-50, date=cls.analyze_end_date, tags=[cls.tag_groceries]
        )

        cls.trans = Transaction.objects.all()

    def setUp(self) -> None:
        self.predictor = Predictor(
            analyze_range=(self.analyze_start_date, self.analyze_end_date),
            prediction_range=(self.predict_start_date, self.predict_end_date),
        )

    def test_average(self):
        self.assertEqual(self.predictor._get_average_amount(), (-300) / 4)

    def test_odds_of_transaciton_occurence(self):
        self.assertEqual(self.predictor._get_odds_of_transaction_occurence(), 4 / 6)

    def test_get_unique_budgets(self):
        not_included = self.generate_budget()
        unique_budgets = self.predictor._get_unique_budgets()

        expected_budgets = Budget.objects.exclude(pk=not_included.pk)
        self.assertLengthEqual(unique_budgets, len(expected_budgets))
        for budget in expected_budgets:
            self.assertIn(budget, unique_budgets)

    def test_get_unique_tags(self):
        not_included = self.generate_tag()
        unique_tags = self.predictor._get_unique_tags()

        expected_tags = Tag.objects.exclude(pk=not_included.pk)
        self.assertLengthEqual(unique_tags, len(expected_tags))
        for tag in expected_tags:
            self.assertIn(tag, unique_tags)

    def test_tag_odds_distribution(self):
        self.assertEqual(
            self.predictor._get_tag_odds_distribution(),
            {
                self.tag_cool_ranch: 0.25,
                self.tag_groceries: 0.5,
                self.tag_rent: 0.25,
            },
        )

    def test_budget_odds_distribution(self):
        self.assertEqual(
            self.predictor._get_budget_odds_distribution(),
            {
                self.housing: 0.25,
                self.food: 0.5,
                self.doritos: 0.25,
            },
        )
