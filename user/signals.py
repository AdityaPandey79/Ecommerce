# user/signals.py

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .tasks import send_welcome_email_task
from .tasks import send_inactive_users_email_task

@receiver(user_logged_in)
def send_welcome_email(sender, request, user, **kwargs):
    # Trigger email sending in background
    send_welcome_email_task.delay(user.id)

@receiver(user_logged_in)
def send_inactive_users_email(sender, request, user, **kwargs):
    # Call the Celery task asynchronously
    send_inactive_users_email_task.delay()