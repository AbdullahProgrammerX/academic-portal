"""Revision URLs."""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.RevisionListView.as_view(), name='revision_list'),
]
