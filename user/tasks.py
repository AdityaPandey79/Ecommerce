# user/tasks.py
from django.contrib.auth.models import User
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from django.utils import timezone   
import logging

logger = logging.getLogger(__name__)


@shared_task (name='send_welcome_email_task')
def send_welcome_email_task(user_id):
    logger.info(f"[TASK STARTED] Processing user ID {user_id}")

    try:
        logger.debug(f"[FETCHING USER] ID {user_id}")
        user = User.objects.get(pk=user_id)

        logger.info(f"[USER FOUND] {user.username} | Email: {user.email or 'No email'}")

        subject = 'Welcome Back!'
        message = (
            f"Hi {user.username},\n\n"
            "Welcome back to our store!\n"
            "Hope you find what you're looking for.\n\n"
            "Best regards,\n"
            "The E-Commerce Team"
        )
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]

        if user.email:
            send_mail(subject, message, from_email, recipient_list)
            logger.info(f"Welcome email sent to {user.email}")
            return f"Welcome email sent to {user.email}"
        else:
            logger.warning(f"[NO EMAIL] for user ID {user_id}")
            return f"No email found for {user.username}"

    except User.DoesNotExist:
        logger.error(f"[USER NOT FOUND] ID {user_id}")
        return f"User with ID {user_id} does not exist. Email not sent."
    
@shared_task(name='send_inactive_users_email_task')
def send_inactive_users_email_task():
    try:
        logger.info("[TASK STARTED] Sending inactive user emails")
        one_day_ago = timezone.now() - timedelta(days=1)
        logger.info(f"Querying users with last_login < {one_day_ago}")

        inactive_users = User.objects.filter(last_login__lt=one_day_ago).exclude(email='')
        logger.info(f"Found {inactive_users.count()} inactive users")

        if inactive_users.exists():
            for user in inactive_users:
                logger.info(f"Inactive user: {user.username} (last_login: {user.last_login})")
                subject = "We Miss You!"
                message = (
                    f"Hi {user.username},\n\n"
                    "It's been a while since you visited us.\n"
                    "Come back and see what's new!\n\n"
                    "Best regards,\n"
                    "The E-Commerce Team"
                )
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [user.email]

                try:
                    send_mail(subject, message, from_email, recipient_list)
                    logger.info(f"Inactive user email sent to {user.email}")
                except Exception as e:
                    logger.error(f"Failed to send email to {user.email}: {str(e)}", exc_info=True)
        else:
            logger.info("No inactive users found.")

        return f"Sent re-engagement email to {inactive_users.count()} users"

    except Exception as e:
        logger.error(f"Error sending inactive user emails: {str(e)}", exc_info=True)
        return f"Task failed: {str(e)}"