from django.contrib import admin
from .models import *


@admin.register(Transaction, Category)
class BudgetAdmin(admin.ModelAdmin):
    pass
