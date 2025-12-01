from django.urls import path
from . import views

urlpatterns = [
    # Landing / Dashboard
    path('', views.landing_page, name='landing'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Requests
    path('requests/<int:id>/', views.request_detail, name='request_detail'),
    path('requests/<int:id>/edit/', views.edit_request, name='edit_request'),
    path('requests/<int:id>/delete/', views.delete_request, name='delete_request'),
    path('add/', views.add_request, name='add_request'),
    path('create-category/', views.create_category, name='create_category'),

    # # Categories and Tags (if you have function-based views for them)
    # path('categories/', views.category_list, name='category-list'),
    # path('tags/', views.tag_list, name='tag-list'),
]
