from django.contrib import admin
from .models import Topic, Entry, Expense, Income, FinancialGoal, Profile

# Register your models here.


admin.site.register(Topic)
admin.site.register(Entry)
admin.site.register(Expense)
admin.site.register(Income)
admin.site.register(FinancialGoal)
admin.site.register(Profile)