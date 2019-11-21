from django.contrib import admin
from .models import *


@admin.register(Transaction, Budget, Profile)
class BudgetAdmin(admin.ModelAdmin):
    pass
