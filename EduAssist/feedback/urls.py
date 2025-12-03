from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_feedback, name='submit_feedback'),
    path('my-feedback/', views.my_feedback, name='my_feedback'),
    path('edit/<int:feedback_id>/', views.edit_feedback, name='edit_feedback'),
    path('delete/<int:feedback_id>/', views.delete_feedback, name='delete_feedback'),
]
