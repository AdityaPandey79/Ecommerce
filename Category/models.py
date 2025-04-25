from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='categories_created', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='categories_updated', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name


