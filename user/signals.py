from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings


@receiver(user_logged_in)
def send_welcome_email(sender, request, user, **kwargs):
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

    if user.email:  # Ensure user has an email set
        try:
            send_mail(subject, message, from_email, recipient_list)
            print(f"Welcome email sent to {user.email}")
        except Exception as e:
            print(f" Error sending email to {user.email}: {e}")
