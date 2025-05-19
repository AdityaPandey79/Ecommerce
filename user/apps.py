from django.apps import AppConfig
from django.conf import settings

class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user'

    def ready(self):
        import user.signals  # Connect the login signal
        # if settings.DEBUG:
        #     from user.tasks import send_inactive_users_email_task
        #     send_inactive_users_email_task.delay()