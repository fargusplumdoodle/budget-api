from django.contrib import admin
from .models import *


@admin.register(Transaction, Budget)
class BudgetAdmin(admin.ModelAdmin):
    pass
