from django.shortcuts import render, redirect, get_object_or_404
from .models import Topic, Entry, Expense, Income, FinancialGoal, RecurringExpense
from . forms import TopicForm, EntryForm, ExpenseForm, IncomeForm, FinancialGoalForm, RecurringExpenseForm
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.utils import timezone
from decimal import Decimal

from django.db.models import Count, Sum, Max
# ... existing imports ...

@login_required
def dashboard(request):
    """Show statistics and recent activity."""
    # Statistics
    topic_count = Topic.objects.filter(owner=request.user).count()
    entry_count = Entry.objects.filter(topic__owner=request.user).count()
    
    # Recent entries (last 5)
    recent_entries = Entry.objects.filter(topic__owner=request.user).order_by('-date_added')[:5]
    
    context = {
        'topic_count': topic_count,
        'entry_count': entry_count,
        'recent_entries': recent_entries,
    }
    return render(request, 'learning_logs/dashboard.html', context)




def index(request):
    """The home page for Personal Management."""
    context = {}
    if request.user.is_authenticated:
        now = timezone.now()
        
        # --- 1. Financial Summary ---
        goals, _ = FinancialGoal.objects.get_or_create(owner=request.user)
        
        # Income
        monthly_income = Income.objects.filter(
            owner=request.user, 
            date_added__year=now.year, 
            date_added__month=now.month
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        total_income = goals.monthly_salary + monthly_income
        
        # Expenses
        expenses = Expense.objects.filter(
            owner=request.user, 
            date_added__year=now.year, 
            date_added__month=now.month
        )
        total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
        balance = total_income - total_expenses
        
        # --- 2. Notifications (Daily Expenses) ---
        has_expenses_today = expenses.filter(date_added__date=now.date()).exists()
        notifications = []
        if not has_expenses_today:
            notifications.append("Leo bado hujaweka matumizi yako. Kumbuka kurekodi!")
            
        # --- 3. Continue Learning (Recent Topics) ---
        recent_topics = Topic.objects.filter(owner=request.user).annotate(
            last_activity=Max('entry__date_added')
        ).order_by('-last_activity')[:3]
        
        context = {'total_income': total_income, 'total_expenses': total_expenses, 'balance': balance, 'notifications': notifications, 'recent_topics': recent_topics}
        
    return render(request, 'learning_logs/index.html', context)

@login_required
def topics(request):
    """Show all topics."""
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics': topics}
    return render(request, 'learning_logs/topics.html', context)


@login_required
def topic(request, topic_id):
      """Show a single topic and all its entries."""
      topic = Topic.objects.get(id=topic_id)
      # Make sure the topic belongs to the current user.
      if topic.owner != request.user:
          raise Http404
      entries = topic.entry_set.order_by('-date_added')
      context = {'topic': topic, 'entries': entries}
      return render(request, 'learning_logs/topic.html', context)


@login_required
def new_topic(request):
    """Add a new topic."""
    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = TopicForm()
    else:
        # POST data submitted; process data.
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return redirect('learning_logs:topics')
    # Display a blank or invalid form.
    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)


@login_required
def new_entry(request, topic_id):
    """Add a new entry for a particular topic."""
    topic = Topic.objects.get(id=topic_id)
 
    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = EntryForm()
    else:
        # POST data submitted; process data.
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return redirect('learning_logs:topic', topic_id=topic_id)
    # Display a blank or invalid form.
    context = {'topic': topic, 'form': form}
    return render(request, 'learning_logs/new_entry.html', context)

@login_required
def edit_entry(request, entry_id):
    """Edit an existing entry."""
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    if topic.owner != request.user:
        raise Http404

    if request.method != 'POST':
        # Initial request; pre-fill form with the current entry.
        form = EntryForm(instance=entry)
    else:
        # POST data submitted; process data.
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('learning_logs:topic', topic_id=topic.id)
        
    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'learning_logs/edit_entry.html', context)

@login_required
def delete_entry(request, entry_id):
    """Delete an existing entry."""
    entry = get_object_or_404(Entry, id=entry_id)
    topic = entry.topic

    # Make sure the entry belongs to the current user.
    if topic.owner != request.user:
        raise Http404

    if request.method == 'POST':
        entry.delete()
        return redirect('learning_logs:topic', topic_id=topic.id)

    return redirect('learning_logs:topic', topic_id=topic.id)

def about(request):
    """Show the about page."""
    return render(request, 'learning_logs/about.html')

def contact(request):
    """Show the contact page."""
    return render(request, 'learning_logs/contact.html')

@login_required
def expenses(request):
    """Show financial dashboard with income, expenses, and goal analysis."""
    now = timezone.now()
    
    # Get or create user's financial goals/settings
    goals, created = FinancialGoal.objects.get_or_create(owner=request.user)
    
    # 1. Calculate Income
    # Actual income entries for this month
    monthly_income_entries = Income.objects.filter(owner=request.user, date_added__year=now.year, date_added__month=now.month)
    actual_income_sum = monthly_income_entries.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Projected income (Salary + Daily Estimate * 30)
    projected_income = goals.monthly_salary + (goals.daily_income_estimate * 30)
    
    # Total Income to use (Base salary + any extra added income)
    # If they have a salary, we assume it's part of the plan, plus any extra 'Income' entries
    # If they rely on daily income, 'actual_income_sum' tracks what they've actually logged.
    total_income_so_far = goals.monthly_salary + actual_income_sum

    # 2. Calculate Expenses
    expenses = Expense.objects.filter(owner=request.user, date_added__year=now.year, date_added__month=now.month).order_by('-date_added')
    total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # 3. Analysis
    balance = total_income_so_far - total_expenses
    
    # Daily Analysis
    today_expenses = expenses.filter(date_added__date=now.date()).aggregate(Sum('amount'))['amount__sum'] or 0
    daily_limit_status = "Good"
    if goals.daily_spending_limit > 0 and today_expenses > goals.daily_spending_limit:
        daily_limit_status = "Exceeded"
        
    # 4. Recurring Expenses
    recurring_expenses = RecurringExpense.objects.filter(owner=request.user).order_by('next_due_date')
    
    # 5. AI Suggestions Logic
    suggestions = []
    if balance < 0:
        suggestions.append({"type": "danger", "icon": "fa-exclamation-triangle", "text": "Tahadhari: Umetumia zaidi ya mapato yako mwezi huu! Angalia matumizi yako ya anasa."})
    elif balance < (total_income_so_far * Decimal('0.1')) and total_income_so_far > 0:
        suggestions.append({"type": "warning", "icon": "fa-lightbulb", "text": "Ushauri: Akiba yako ni ndogo. Jaribu kuweka akiba angalau 10% ya mapato yako."})
    elif balance > (total_income_so_far * Decimal('0.3')):
        suggestions.append({"type": "success", "icon": "fa-chart-line", "text": "Vizuri sana! Unaweka akiba nzuri. Fikiria kuwekeza kiasi hiki."})

    if daily_limit_status == "Exceeded":
        suggestions.append({"type": "danger", "icon": "fa-hand-holding-usd", "text": "Umezidi bajeti yako ya siku. Punguza matumizi yasiyo ya lazima leo."})
    
    recurring_total = recurring_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    if goals.monthly_salary > 0 and recurring_total > (goals.monthly_salary * Decimal('0.5')):
         suggestions.append({"type": "warning", "icon": "fa-file-invoice-dollar", "text": "Matumizi ya kudumu (kodi, vifurushi) yanachukua zaidi ya 50% ya mshahara wako."})

    if not suggestions:
        suggestions.append({"type": "info", "icon": "fa-robot", "text": "Mfumo unaendelea kujifunza kutokana na matumizi yako. Endelea kurekodi!"})

    # 6. Chart Data (Last 7 Days)
    last_7_days = [now.date() - timezone.timedelta(days=i) for i in range(6, -1, -1)]
    chart_labels = [day.strftime('%a %d') for day in last_7_days]
    chart_data = []
    for day in last_7_days:
        day_expenses = Expense.objects.filter(owner=request.user, date_added__date=day).aggregate(Sum('amount'))['amount__sum'] or 0
        chart_data.append(float(day_expenses))

    # 7. Pie Chart Data (Expenses by Category)
    expenses_by_category = Expense.objects.filter(
        owner=request.user, 
        date_added__year=now.year, 
        date_added__month=now.month
    ).values('category').annotate(total=Sum('amount')).order_by('-total')
    
    pie_labels = [item['category'] for item in expenses_by_category]
    pie_data = [float(item['total']) for item in expenses_by_category]

    context = {
        'expenses': expenses,
        'goals': goals,
        'total_income': total_income_so_far,
        'total_expenses': total_expenses,
        'balance': balance,
        'today_expenses': today_expenses,
        'daily_limit_status': daily_limit_status,
        'projected_income': projected_income,
        'recurring_expenses': recurring_expenses,
        'suggestions': suggestions,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'pie_labels': pie_labels,
        'pie_data': pie_data,
    }
    return render(request, 'learning_logs/expenses.html', context)

@login_required
def new_expense(request):
    """Add a new expense."""
    if request.method != 'POST':
        form = ExpenseForm()
    else:
        form = ExpenseForm(data=request.POST)
        if form.is_valid():
            new_expense = form.save(commit=False)
            new_expense.owner = request.user
            new_expense.save()
            return redirect('learning_logs:expenses')
    context = {'form': form}
    return render(request, 'learning_logs/new_expense.html', context)

@login_required
def edit_expense(request, expense_id):
    """Edit an existing expense."""
    expense = get_object_or_404(Expense, id=expense_id)
    if expense.owner != request.user:
        raise Http404

    if request.method != 'POST':
        form = ExpenseForm(instance=expense)
    else:
        form = ExpenseForm(instance=expense, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('learning_logs:expenses')
    context = {'expense': expense, 'form': form}
    return render(request, 'learning_logs/edit_expense.html', context)

@login_required
def delete_expense(request, expense_id):
    """Delete an expense."""
    expense = get_object_or_404(Expense, id=expense_id)
    if expense.owner == request.user:
        expense.delete()
    return redirect('learning_logs:expenses')

@login_required
def financial_goals(request):
    """Manage financial goals and settings."""
    goals, created = FinancialGoal.objects.get_or_create(owner=request.user)
    
    if request.method != 'POST':
        form = FinancialGoalForm(instance=goals)
    else:
        form = FinancialGoalForm(instance=goals, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('learning_logs:expenses')
            
    context = {'form': form}
    return render(request, 'learning_logs/financial_goals.html', context)

@login_required
def new_income(request):
    """Add a new income entry."""
    if request.method != 'POST':
        form = IncomeForm()
    else:
        form = IncomeForm(data=request.POST)
        if form.is_valid():
            new_income = form.save(commit=False)
            new_income.owner = request.user
            new_income.save()
            return redirect('learning_logs:expenses')
    context = {'form': form}
    return render(request, 'learning_logs/new_income.html', context)

@login_required
def new_recurring_expense(request):
    """Add a new recurring expense."""
    if request.method != 'POST':
        form = RecurringExpenseForm()
    else:
        form = RecurringExpenseForm(data=request.POST)
        if form.is_valid():
            new_re = form.save(commit=False)
            new_re.owner = request.user
            new_re.save()
            return redirect('learning_logs:expenses')
    context = {'form': form}
    return render(request, 'learning_logs/new_recurring_expense.html', context)

@login_required
def delete_recurring_expense(request, expense_id):
    """Delete a recurring expense."""
    expense = get_object_or_404(RecurringExpense, id=expense_id)
    if expense.owner == request.user:
        expense.delete()
    return redirect('learning_logs:expenses')