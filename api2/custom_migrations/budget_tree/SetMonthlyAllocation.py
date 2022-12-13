from budget.utils.migrations import CustomMigration


class SetMonthlyAllocation(CustomMigration):
    def forward(self):
        Budget = self.get_model("api2", "Budget")

        for budget in Budget.objects.using(self.db).all():
            budget.monthly_allocation = abs(
                budget.outcome_per_month if budget.outcome_per_month else 0
            )
            budget.save()

    def reverse(self):
        pass
