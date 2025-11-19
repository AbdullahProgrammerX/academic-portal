"""
Celery configuration for editorial_system.
"""
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('editorial_system')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Periodic tasks
app.conf.beat_schedule = {
    'cleanup-expired-presigned-urls': {
        'task': 'files.tasks.cleanup_expired_urls',
        'schedule': crontab(hour=2, minute=0),  # Run at 2 AM daily
    },
    'send-reminder-emails': {
        'task': 'submissions.tasks.send_review_reminders',
        'schedule': crontab(hour=9, minute=0),  # Run at 9 AM daily
    },
}
