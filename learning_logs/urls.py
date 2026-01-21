"""Defines URL patterns for Personal Management."""
from django.urls import path
from . import views

app_name = 'learning_logs'

urlpatterns = [
  # Home page
  path('', views.index, name='index'),
  # Page that shows all topics.
  path('topics/', views.topics, name='topics'),
  # individual page
  path('topics/<int:topic_id>/', views.topic, name='topic'),
  # Page for adding a new topic
  path('new_topic/', views.new_topic, name='new_topic'),
  # Page for adding a new entry
  path('new_entry/<int:topic_id>/', views.new_entry, name='new_entry'),
  # Page for editing an entry.
  path('edit_entry/<int:entry_id>/', views.edit_entry, name='edit_entry'),
  # Page for deleting an entry.
  path('delete_entry/<int:entry_id>/', views.delete_entry, name='delete_entry'),
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
]