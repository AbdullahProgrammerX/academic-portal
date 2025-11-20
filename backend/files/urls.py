"""File URLs."""
from django.urls import path
from . import views

urlpatterns = [
    path('presigned-url/', views.GetPresignedUploadView.as_view(), name='presigned_upload'),
    path('download/<uuid:file_id>/', views.DownloadFileView.as_view(), name='download_file'),
]
