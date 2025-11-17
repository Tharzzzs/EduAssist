# request/urls.py - Update this file
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Initialize Default Router for DRF ViewSets
router = DefaultRouter()
router.register(r'api/requests', views.RequestViewSet, basename='request-api')
router.register(r'api/categories', views.CategoryViewSet, basename='category-api')
router.register(r'api/tags', views.TagViewSet, basename='tag-api')

urlpatterns = [
    # Function-based views (F-BVs) - for legacy/specific pages
    path('dashboard/', views.dashboard_view, name='dashboard'), # Legacy dashboard
    path('requests/<int:id>/', views.request_detail, name='request_detail'), # Legacy detail
    path('requests/<int:id>/edit/', views.edit_request, name='edit_request'), # Legacy edit
    path('requests/<int:id>/delete/', views.delete_request, name='delete_request'), # Legacy delete
    path('add/', views.add_request, name='add_request'), # Legacy add
    path('', views.landing_page, name='landing'),

    # Class-based views (C-BVs) - Modern list/CRUD
    # Note: Using RequestListView as the primary request list now
    path('list/', views.RequestListView.as_view(), name='request-list'),
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('tags/', views.TagListView.as_view(), name='tag-list'),
    path('create/', views.RequestCreateView.as_view(), name='request-create'),
    path('<int:pk>/', views.RequestDetailView.as_view(), name='request-detail'),
    path('<int:pk>/update/', views.RequestUpdateView.as_view(), name='request-update'),
    path('<int:pk>/delete/', views.RequestDeleteView.as_view(), name='request-delete'),

    # API URLs
    path('', include(router.urls)),
]