from django import forms
from .models import Topic, Entry, Expense, Income, FinancialGoal, RecurringExpense


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['text']
        labels = {'text': ''}

class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['text']
        labels = {'text': 'Entry:'}
        widgets = {'text': forms.Textarea(attrs={'cols': 80})}

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'amount', 'category']
        labels = {'title': 'Maelezo ya Matumizi', 'amount': 'Kiasi (TZS)', 'category': 'Kundi'}

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['source', 'amount']
        labels = {'source': 'Chanzo cha Mapato (Mf. Mshahara, Mauzo)', 'amount': 'Kiasi (TZS)'}

class FinancialGoalForm(forms.ModelForm):
    class Meta:
        model = FinancialGoal
        fields = ['monthly_salary', 'daily_income_estimate', 'savings_goal', 'daily_spending_limit']
        labels = {
            'monthly_salary': 'Mshahara wa Mwezi (Kama umeajiriwa)',
            'daily_income_estimate': 'Makadirio ya Mapato ya Siku (Kama huna mshahara maalum)',
            'savings_goal': 'Lengo la Akiba kwa Mwezi',
            'daily_spending_limit': 'Kiwango cha Juu cha Matumizi kwa Siku (Bajeti)'
        }

class RecurringExpenseForm(forms.ModelForm):
    class Meta:
        model = RecurringExpense
        fields = ['title', 'amount', 'category', 'frequency', 'next_due_date']
        widgets = {
            'next_due_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'title': 'Jina la Matumizi (Mf. Kodi, Netflix)',
            'amount': 'Kiasi (TZS)',
            'category': 'Kundi',
            'frequency': 'Inajirudia',
            'next_due_date': 'Tarehe Ijayo ya Malipo'
        }