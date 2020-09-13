from django.contrib import admin
from api.models import *


@admin.register(Transaction, Budget)
class BudgetAdmin(admin.ModelAdmin):
    pass
