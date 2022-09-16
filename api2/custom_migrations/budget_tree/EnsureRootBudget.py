from api2.constants import ROOT_BUDGET_NAME
from budget.utils.migrations import CustomMigration


class EnsureRootBudget(CustomMigration):
    def create_root_budget(self, UserInfo, Budget):
        for user_info in UserInfo.objects.using(self.db).all():
            Budget.objects.using(self.db).get_or_create(
                name=ROOT_BUDGET_NAME,
                user=user_info.user,
            )

    def put_all_budgets_under_root(self, Budget):
        orphan_budgets = (
            Budget.objects.using(self.db)
            .filter(parent=None)
            .exclude(name=ROOT_BUDGET_NAME)
        )

        for budget in orphan_budgets:
            budget.parent = Budget.objects.using(self.db).get(
                user=budget.user, name=ROOT_BUDGET_NAME
            )
            budget.save()

    def forward(self):
        Budget = self.get_model("api2", "Budget")
        UserInfo = self.get_model("api2", "UserInfo")

        self.create_root_budget(UserInfo, Budget)
        self.put_all_budgets_under_root(Budget)

    def reverse(self):
        pass
