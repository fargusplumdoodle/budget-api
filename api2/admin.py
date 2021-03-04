from django.contrib import admin
from api2.models import Transaction, Budget


@admin.register(Transaction, Budget)
class BudgetAdmin(admin.ModelAdmin):
    pass
