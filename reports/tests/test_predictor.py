from unittest.mock import patch
import arrow
from django.contrib.auth.models import User
from django.db.models import QuerySet

from api2.constants import ROOT_BUDGET_NAME
from api2.models import Budget, Tag, Transaction
from budget.utils.test import BudgetTestCase
from reports.predictor import Predictor
from reports.utils import daysBetween

PREDICTOR_MODULE = "reports.predictor"


class TestPredictor(BudgetTestCase):
    analyze_end_date: arrow.Arrow
    analyze_start_date: arrow.Arrow
    predict_start_date: arrow.Arrow
    predict_end_date: arrow.Arrow
    user: User
    trans: "QuerySet[Transaction]"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.housing = cls.generate_budget(
            name="housing", parent=cls.root, monthly_allocation=50
        )
        cls.doritos = cls.generate_budget(
            name="doritos", parent=cls.root, monthly_allocation=25
        )
        cls.food = cls.generate_budget(
            name="food", parent=cls.root, monthly_allocation=25
        )

        cls.tag_rent = cls.generate_tag(name="rent")
        cls.tag_cool_ranch = cls.generate_tag(name="cool ranch")
        cls.tag_groceries = cls.generate_tag(name="groceries")
        cls.tag_skip = cls.generate_tag(name="skip")

        cls.analyze_start_date = arrow.get(2022, 1, 1)
        cls.analyze_end_date = arrow.get(2022, 1, 7)

        cls.predict_start_date = arrow.get(2022, 1, 8)
        cls.predict_end_date = arrow.get(2022, 1, 14)

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
            cls.food, amount=-25, date=cls.analyze_end_date, tags=[cls.tag_groceries]
        )
        cls.generate_transaction(
            cls.food,
            amount=-25,
            date=cls.analyze_end_date.shift(days=-1),
            tags=[cls.tag_skip],
        )
        cls.trans = Transaction.objects.all()

    def setUp(self) -> None:
        self.predictor = Predictor(
            self.user,
            analyze_range=(self.analyze_start_date, self.analyze_end_date),
            prediction_range=(self.predict_start_date, self.predict_end_date),
        )

    def test_average(self):
        self.assertEqual(
            self.predictor._get_average_amount(self.trans), (-300) / self.trans.count()
        )

    def test_odds_of_transaciton_occurence(self):
        self.assertEqual(
            self.predictor._get_odds_of_transaction_occurence(self.trans),
            self.trans.count()
            / daysBetween((self.analyze_start_date, self.analyze_end_date)),
        )

    def test_get_unique_budgets(self):
        not_included = self.generate_budget()
        unique_budgets = self.predictor._get_unique_budgets()

        expected_budgets = Budget.objects.exclude(pk=not_included.pk).exclude(name=ROOT_BUDGET_NAME)
        self.assertLengthEqual(unique_budgets, len(expected_budgets))
        for budget in expected_budgets:
            self.assertIn(budget, unique_budgets)

    def test_get_unique_tags(self):
        not_included = self.generate_tag()
        unique_tags = self.predictor._get_unique_tags(self.trans)

        expected_tags = Tag.objects.exclude(pk=not_included.pk)
        self.assertLengthEqual(unique_tags, len(expected_tags))
        for tag in expected_tags:
            self.assertIn(tag, unique_tags)

    def test_tag_odds_distribution(self):
        total_trans = self.trans.count()

        def get_odds(tag: Tag):
            return self.trans.filter(tags=tag).count() / total_trans

        self.assertEqual(
            self.predictor._get_tag_odds_distribution(self.trans),
            {
                self.tag_cool_ranch: get_odds(self.tag_cool_ranch),
                self.tag_groceries: get_odds(self.tag_groceries),
                self.tag_skip: get_odds(self.tag_skip),
                self.tag_rent: get_odds(self.tag_rent),
            },
        )

    def test_budget_odds_distribution(self):
        total_trans = self.trans.count()

        def get_odds(budget: Budget):
            return self.trans.filter(budget=budget).count() / total_trans

        self.assertEqual(
            self.predictor._get_budget_odds_distribution(),
            {
                self.housing: get_odds(self.housing),
                self.food: get_odds(self.food),
                self.doritos: get_odds(self.doritos),
            },
        )

    def test_transaction_probability_distrobution(self):
        expected_probability_distrobution = {
            self.doritos: {
                "prob": 0.2,
                "tags": {self.tag_cool_ranch: {"prob": 1.0, "average_amount": -100}},
            },
            self.food: {
                "prob": 0.6,
                "tags": {
                    self.tag_groceries: {"prob": 2 / 3, "average_amount": -38},
                    self.tag_skip: {"prob": 1 / 3, "average_amount": -25},
                },
            },
            self.housing: {
                "prob": 0.2,
                "tags": {self.tag_rent: {"prob": 1.0, "average_amount": -100}},
            },
        }
        self.assertEqual(
            expected_probability_distrobution,
            self.predictor.transaction_probability_distrobution,
        )

    def test_get_transactions_to_create_per_day(self):
        # The ratio of transactions created per day will be less than one by default
        with patch(f"{PREDICTOR_MODULE}.roll", return_value=True):
            self.assertEqual(self.predictor._get_transactions_to_create_per_day(), 1)

        with patch(f"{PREDICTOR_MODULE}.roll", return_value=False):
            self.assertEqual(self.predictor._get_transactions_to_create_per_day(), 0)

        self.predictor.transactions_in_analysis_period += (
            self.predictor.days_in_analysis_period
        )

        with patch(f"{PREDICTOR_MODULE}.roll", return_value=True):
            self.assertEqual(self.predictor._get_transactions_to_create_per_day(), 2)

        with patch(f"{PREDICTOR_MODULE}.roll", return_value=False):
            self.assertEqual(self.predictor._get_transactions_to_create_per_day(), 1)

    def test_generate_transactions(self):
        predicted_transactions = self.predictor._generate_transactions()

        for trans in predicted_transactions:
            self.assertTrue(trans.prediction)
            self.assertFalse(trans.income)
            self.assertFalse(trans.transfer)
            self.assertEqual(trans.description, "prediction")
            self.assertTrue(
                self.predict_start_date
                <= arrow.get(trans.date)
                <= self.predict_end_date
            )

    def test_generate_income_transactions(self):
        predicted_income = self.predictor._generate_income_transactions()
        for trans in predicted_income:
            self.assertTrue(trans.income)
            self.assertTrue(trans.prediction)
            self.assertFalse(trans.transfer)
