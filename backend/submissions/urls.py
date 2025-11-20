"""Submission URLs with DRF Router."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'submissions', views.SubmissionViewSet, basename='submission')
router.register(r'authorships', views.AuthorshipViewSet, basename='authorship')

urlpatterns = [
    path('', include(router.urls)),
]
