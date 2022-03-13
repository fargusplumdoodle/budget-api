from unittest import skip
from budget.utils.test import BudgetTestCase
from reports.utils import roll


class TestRoll(BudgetTestCase):
    @skip("Not exact enough to test properly")
    def test(self):
        trials = 1000_000
        prob = 5 / 6
        yes = no = 0
        for _ in range(trials):
            passed = roll(prob)
            if passed:
                yes += 1
            else:
                no += 1
        print("outcome", yes / trials)
