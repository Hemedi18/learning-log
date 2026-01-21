from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.core.serializers import serialize
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Topic, Entry, Expense, Income, FinancialGoal, RecurringExpense, AccessLog, Profile
from . forms import TopicForm, EntryForm, ExpenseForm, IncomeForm, FinancialGoalForm, RecurringExpenseForm, ProfileForm
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.utils import timezone
from django.db.models import Q
from .utils import XCalendar
import datetime
import json
from decimal import Decimal
from datetime import timedelta

from django.db.models import Count, Sum, Max
# ... existing imports ...

@login_required
def dashboard(request):
    """Show statistics and recent activity."""
    # Statistics
    topic_count = Topic.objects.filter(owner=request.user).count()
    entry_count = Entry.objects.filter(owner=request.user).count()
    
    # Recent entries (last 5)
    recent_entries = Entry.objects.filter(owner=request.user).order_by('-date_created')[:5]
    
    # Analytics: Sentiment Trends (Last 30 Days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    entries_last_30 = Entry.objects.filter(
        owner=request.user,
        date_created__gte=thirty_days_ago
    ).exclude(mood='').order_by('date_created')
    
    mood_map = {'Happy': 10, 'Excited': 8, 'Neutral': 5, 'Anxious': 3, 'Sad': 1}
    sentiment_trend = []
    
    for entry in entries_last_30:
        sentiment_trend.append({
            'date': entry.date_created.strftime('%Y-%m-%d'),
            'score': mood_map.get(entry.mood, 5)
        })

    context = {
        'topic_count': topic_count,
        'entry_count': entry_count,
        'recent_entries': recent_entries,
        'sentiment_trend': sentiment_trend,
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
        
        # Bill Reminders
        upcoming_bills = RecurringExpense.objects.filter(
            owner=request.user,
            reminder_active=True,
            next_due_date__range=[now.date(), now.date() + timedelta(days=3)]
        )
        for bill in upcoming_bills:
            days_left = (bill.next_due_date - now.date()).days
            if days_left == 0:
                notifications.append(f"Kikumbusho: {bill.title} inatakiwa kulipwa leo (TZS {bill.amount})")
            else:
                notifications.append(f"Kikumbusho: {bill.title} inatakiwa kulipwa baada ya siku {days_left}")
            
        # --- 3. Recent Diary Entries ---
        recent_entries = Entry.objects.filter(owner=request.user).order_by('-date_created')[:3]
        
        context = {'total_income': total_income, 'total_expenses': total_expenses, 'balance': balance, 'notifications': notifications, 'recent_entries': recent_entries}
        
    return render(request, 'learning_logs/index.html', context)

# --- Diary Class-Based Views ---

class EntryListView(LoginRequiredMixin, ListView):
    model = Entry
    template_name = 'learning_logs/entry_list.html'
    context_object_name = 'entries'
    ordering = ['-date_created']

    def get_queryset(self):
        # Enterprise Optimization: Prefetch related tags and health matrix to reduce DB queries
        queryset = Entry.objects.filter(owner=self.request.user)\
            .prefetch_related('tags', 'health_matrix')\
            .order_by('-date_created')
        
        # Search Engine Logic
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(tags__name__icontains=query) |
                Q(mood__icontains=query)
            ).distinct()
            
        return queryset

    def get(self, request, *args, **kwargs):
        # Security Log
        AccessLog.objects.create(user=self.request.user, action="Viewed Entry List", ip_address=self.request.META.get('REMOTE_ADDR'))
        return super().get(request, *args, **kwargs)

class EntryDetailView(LoginRequiredMixin, DetailView):
    model = Entry
    template_name = 'learning_logs/entry_detail.html'
    context_object_name = 'entry'

    def get_queryset(self):
        return Entry.objects.filter(owner=self.request.user)

class EntryCreateView(LoginRequiredMixin, CreateView):
    model = Entry
    fields = ['title', 'content', 'mood']
    template_name = 'learning_logs/entry_form.html'
    success_url = reverse_lazy('learning_logs:entry_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class EntryUpdateView(LoginRequiredMixin, UpdateView):
    model = Entry
    fields = ['title', 'content', 'mood']
    template_name = 'learning_logs/entry_form.html'
    success_url = reverse_lazy('learning_logs:entry_list')

    def get_queryset(self):
        return Entry.objects.filter(owner=self.request.user)

class EntryDeleteView(LoginRequiredMixin, DeleteView):
    model = Entry
    success_url = reverse_lazy('learning_logs:entry_list')
    template_name = 'learning_logs/entry_confirm_delete.html'
    
    def get_queryset(self):
        return Entry.objects.filter(owner=self.request.user)

class CalendarView(LoginRequiredMixin, TemplateView):
    template_name = 'learning_logs/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Temporal Navigation
        d = get_date(self.request.GET.get('month', None))
        cal = XCalendar(d.year, d.month, user=self.request.user)
        html_cal = cal.formatmonth(withyear=True)
        
        context['calendar'] = html_cal
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        context['form'] = EntryForm() # Pass form for the modal
        return context

@login_required
def calendar_data(request):
    """API to fetch calendar HTML for AJAX navigation."""
    year = request.GET.get('year')
    month = request.GET.get('month')
    if year and month:
        cal = XCalendar(int(year), int(month), user=request.user)
        html_cal = cal.formatmonth(withyear=True)
        return HttpResponse(html_cal)
    return HttpResponse('Invalid parameters', status=400)

@login_required
def export_data(request):
    """Export diary entries to JSON for data portability."""
    entries = Entry.objects.filter(owner=request.user).prefetch_related('tags')
    data = serialize('json', entries, use_natural_foreign_keys=True)
    response = HttpResponse(data, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="diary_export.json"'
    return response

@login_required
def autosave_entry(request):
    """API endpoint for auto-saving drafts via fetch."""
    if request.method == 'POST':
        # Logic to handle draft saving would go here
        return JsonResponse({'status': 'success', 'message': 'Draft saved securely'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def update_entry_date(request):
    """API to update an entry's date via drag-and-drop."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            entry_id = data.get('entry_id')
            date_str = data.get('date')
            
            entry = Entry.objects.get(id=entry_id, owner=request.user)
            new_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Update date while preserving time
            entry.event_date = entry.event_date.replace(year=new_date.year, month=new_date.month, day=new_date.day)
            entry.save()
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=405)

def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return datetime.date(year, month, day=1)
    return datetime.datetime.today()

def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - datetime.timedelta(days=1)
    return f"month={prev_month.year}-{prev_month.month}"

def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + datetime.timedelta(days=1)
    return f"month={next_month.year}-{next_month.month}"

import calendar

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
    goals, created = FinancialGoal.objects.get_or_create(owner=request.user) #FinancialGoal is kept as this model and form is not meant to be changed
    
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
    
    # Savings Progress Calculation
    savings_progress = 0
    if goals.savings_goal > 0:
        savings_progress = (balance / goals.savings_goal) * 100
        savings_progress = min(max(savings_progress, 0), 100) # Clamp between 0 and 100
    
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
        'savings_progress': savings_progress,
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
def profile(request):
    """User profile page to manage settings and goals."""
    goals, created = FinancialGoal.objects.get_or_create(owner=request.user)
    profile, created_profile = Profile.objects.get_or_create(user=request.user)
    
    # Initialize forms
    form = FinancialGoalForm(instance=goals)
    p_form = ProfileForm(instance=profile)
    password_form = PasswordChangeForm(request.user)
    
    if request.method == 'POST':
        if 'submit_financial' in request.POST:
            form = FinancialGoalForm(instance=goals, data=request.POST)
            if form.is_valid():
                form.save()
                return redirect('learning_logs:profile')
        elif 'submit_profile' in request.POST:
            p_form = ProfileForm(request.POST, request.FILES, instance=profile)
            if p_form.is_valid():
                p_form.save()
                return redirect('learning_logs:profile')
        elif 'submit_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                return redirect('learning_logs:profile')
            
    context = {'user': request.user, 'form': form, 'p_form': p_form, 'password_form': password_form}
    return render(request, 'learning_logs/profile.html', context)

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