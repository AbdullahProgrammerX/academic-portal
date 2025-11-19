"""Submission URLs."""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.SubmissionListView.as_view(), name='submission_list'),
    path('create/', views.SubmissionCreateView.as_view(), name='submission_create'),
]
