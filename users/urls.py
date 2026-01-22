"""Defines URL patterns for users"""
from django.urls import path, include
from . import views

app_name = 'users'

urlpatterns = [
    # Registration page.
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Include default auth urls.
    path('', include('django.contrib.auth.urls')),
]