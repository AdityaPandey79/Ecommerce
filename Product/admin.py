from django.contrib import admin
from .models import Product

# Register your models here.
admin.site.register(Product)
Product.objects.count()

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'name', 'description', 'price', 'category', 'is_active', 'created_by', 'created_at', 'updated_by', 'updated_at')
    list_filter = ('is_active', 'category', 'created_by')
    search_fields = ('name', 'description', 'category__name')
    ordering = ('created_at',)
    list_per_page = 20

