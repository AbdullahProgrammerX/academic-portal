"""
Celery tasks for async processing.
"""
from celery import shared_task


@shared_task
def extract_metadata_from_docx(file_id):
    """Extract metadata from Word document."""
    pass


@shared_task
def extract_metadata_from_pdf(file_id):
    """Extract metadata from PDF document."""
    pass


@shared_task
def send_notification_email(user_id, subject, message):
    """Send notification email to user."""
    pass
