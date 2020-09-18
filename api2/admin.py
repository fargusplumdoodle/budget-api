from django.contrib import admin
from api2.models import *


@admin.register(Transaction, Budget)
class BudgetAdmin(admin.ModelAdmin):
    pass
