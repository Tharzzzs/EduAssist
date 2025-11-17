from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'api/requests', views.RequestViewSet, basename='request-api')
router.register(r'api/categories', views.CategoryListAPI, basename='category-api')
router.register(r'api/tags', views.TagViewSet, basename='tag-api')

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('requests/<int:id>/', views.request_detail, name='request_detail'),
    path('requests/<int:id>/edit/', views.edit_request, name='edit_request'),
    path('requests/<int:id>/delete/', views.delete_request, name='delete_request'),
    path('add/', views.add_request, name='add_request'),
    path('', views.landing_page, name='landing'),

    path('list/', views.RequestListView.as_view(), name='request-list'),
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('tags/', views.TagListView.as_view(), name='tag-list'),
    path('create/', views.RequestCreateView.as_view(), name='request-create'),
    path('<int:pk>/', views.RequestDetailView.as_view(), name='request-detail'),
    path('<int:pk>/update/', views.RequestUpdateView.as_view(), name='request-update'),
    path('<int:pk>/delete/', views.RequestDeleteView.as_view(), name='request-delete'),

    path('', include(router.urls)),
]
