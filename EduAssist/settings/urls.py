# settings/urls.py
from django.urls import path
from . import views
from django.shortcuts import render, redirect


urlpatterns = [
    path('', views.settings_view, name='settings'),  # Settings page
]

# from django.urls import path
# from . import views

# urlpatterns = [
#     path("settings/", views.user_settings, name="settings"),
# ]
