from django.db import models
from django.contrib.auth.models import User
from Category.models import Category
import logging

logger = logging.getLogger(__name__)

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=200)

    description = models.TextField(blank=True, null=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)

    is_active = models.BooleanField(default=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='products_created')

    created_at = models.DateTimeField(auto_now_add=True)

    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='products_updated')
    
    updated_at = models.DateTimeField(auto_now=True)

    quantity = models.PositiveIntegerField(default=50)

    def save(self, *args, **kwargs):
        # Check stock level
        if self.quantity <= 10:
            logger.warning(f"'{self.name}' is about to get out of stock. Current stock: {self.quantity}")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name}--{self.description}--{self.is_active}"