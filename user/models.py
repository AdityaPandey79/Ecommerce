from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, User  # Ensure User is imported

@receiver(post_save, sender=User)
def assign_group(sender, instance, created, **kwargs):
    if created:
        if instance.is_superuser:
            group = Group.objects.get(name='is_admin')
        else:
            group = Group.objects.get(name='is_not_admin')
        instance.groups.add(group)

        # # Set 'is_staff' to True for all users
        # instance.is_staff = True
        # instance.save()

