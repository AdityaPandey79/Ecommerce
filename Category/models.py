from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100,unique=True)

    description = models.TextField(blank=True, default=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories_created', default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories_updated', default=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
            return f"{self.name} - {self.description[:30]}... (Created: {self.created_at}, Updated: {self.updated_at})"


