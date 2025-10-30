from django.urls import path
from . import views


urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('requests/<int:id>/', views.request_detail, name='request_detail'),
    path('requests/<int:id>/edit/', views.edit_request, name='edit_request'),
    path('requests/<int:id>/delete/', views.delete_request, name='delete_request'),
    path('add/', views.add_request, name='add_request'),
    path('', views.landing_page, name='landing'),
]