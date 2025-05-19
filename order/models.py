from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from Category.models import Category  
from Product.models import Product  

class Order(models.Model):
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('dispatched', 'Dispatched'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('out_for_delivery', 'Out for Delivery'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    is_cancelled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Order #{self.id} by {self.user.username}'
    def save(self, *args, **kwargs):
        if self.product and self.quantity:
            self.total_price = self.product.price * self.quantity
        super(Order, self).save(*args, **kwargs)
    def cancel_order(self):
        if not self.is_cancelled:
            # Restore the product's quantity
            self.product.quantity += self.quantity
            self.product.save()

            # Mark the order as canceled
            self.is_cancelled = True