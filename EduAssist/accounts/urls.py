from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('home/', views.home_view, name='home'),
    path('change-password/', views.change_password, name='change_password'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('requests/<int:id>/', views.request_detail, name='request_detail'),
    path('requests/<int:id>/edit/', views.edit_request, name='edit_request'),
    path('requests/<int:id>/delete/', views.delete_request, name='delete_request'),
    path('add/', views.add_request, name='add_request'),
    path('profile/', views.profile, name='profile'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
