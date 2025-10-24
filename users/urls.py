"""Defines URL patterns for users"""
from django.urls import path, include
from . import views

app_name = 'users'

urlpatterns = [
    # Include default auth urls.
    path('logout/', views.logout_view, name='logout'),
    path('', include('django.contrib.auth.urls')),
    # path('logout/', views.logout, name='logout')

    # Registration page.
    path('register/', views.register, name='register'),
]