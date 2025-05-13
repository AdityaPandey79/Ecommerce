from rest_framework import serializers
from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['user', 'order_status', 'created_at', 'updated_at']


class DeliveryStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['order_status']


class CancelOrderSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=255)