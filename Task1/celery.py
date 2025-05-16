# Task1/celery.py

import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab,schedule
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Task1.settings')

app = Celery('Task1')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'daily-inactive-user-email': {
        'task': 'user.tasks.send_inactive_users_email',
        'schedule': timedelta(hours=24),  # can replace with crontab(minute=0, hour=0, day_of_week='mon') for weekly
        'args': (),
    },
}