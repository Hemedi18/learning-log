"""Defines URL patterns for Personal Management."""
from django.urls import path, reverse_lazy
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views

app_name = 'learning_logs'

urlpatterns = [
  # Home page
  path('', views.index, name='index'),
  # Diary URLs (CBVs)
  path('entries/', views.EntryListView.as_view(), name='entry_list'),
  path('entry/<int:pk>/', views.EntryDetailView.as_view(), name='entry_detail'),
  path('entry/new/', views.EntryCreateView.as_view(), name='entry_create'),
  path('entry/<int:pk>/edit/', views.EntryUpdateView.as_view(), name='entry_update'),
  path('entry/<int:pk>/delete/', views.EntryDeleteView.as_view(), name='entry_delete'),
  path('calendar/', views.CalendarView.as_view(), name='calendar'),
  path('api/calendar/', views.calendar_data, name='calendar_data'),
  path('api/autosave/', views.autosave_entry, name='autosave_entry'),
  path('api/update_entry_date/', views.update_entry_date, name='update_entry_date'),
  path('export/', views.export_data, name='export_data'),
  # About page
  path('about/', views.about, name='about'),
  # Contact page
  path('contact/', views.contact, name='contact'),
  # ... inside urlpatterns ...
  path('dashboard/', views.dashboard, name='dashboard'),
  # Finance Management URLs
  path('expenses/', views.expenses, name='expenses'),
  path('new_expense/', views.new_expense, name='new_expense'),
  path('edit_expense/<int:expense_id>/', views.edit_expense, name='edit_expense'),
  path('delete_expense/<int:expense_id>/', views.delete_expense, name='delete_expense'),
  # Income & Goals
  path('financial_goals/', views.financial_goals, name='financial_goals'),
  path('new_income/', views.new_income, name='new_income'),
  # Recurring Expenses
  path('new_recurring_expense/', views.new_recurring_expense, name='new_recurring_expense'),
  path('delete_recurring_expense/<int:expense_id>/', views.delete_recurring_expense, name='delete_recurring_expense'),
  # Profile
  path('profile/', views.profile, name='profile'),
  # Password Reset
  path('password_reset/', auth_views.PasswordResetView.as_view(
      success_url=reverse_lazy('learning_logs:password_reset_done'),
      html_email_template_name='registration/password_reset_email.html',
      email_template_name='registration/password_reset_email_text.html'
  ), name='password_reset'),
  path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
  path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
      success_url=reverse_lazy('learning_logs:password_reset_complete')
  ), name='password_reset_confirm'),
  path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)