# order/views.py

import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Order
from .serializers import OrderSerializer, DeliveryStatusSerializer, CancelOrderSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Initialize logger
logger = logging.getLogger(__name__)


class OrderViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=OrderSerializer,
        responses={201: OrderSerializer}
    )
    @action(detail=False, methods=['post'], url_path='place-order')
    def place_order(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            logger.info(f"Order placed by {request.user.username}: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.warning(f"Failed to place order. Errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        responses={200: OrderSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='my-orders')
    def user_orders(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        logger.info(f"{request.user.username} viewed their orders")
        return Response(serializer.data)

    @swagger_auto_schema(
        responses={200: OrderSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='admin-orders', permission_classes=[IsAdminUser])
    def admin_orders(self, request):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        logger.info(f"Admin {request.user.username} fetched all orders")
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=DeliveryStatusSerializer,
        responses={200: DeliveryStatusSerializer}
    )
    @action(detail=True, methods=['patch'], url_path='update-delivery-status', permission_classes=[IsAdminUser])
    def update_delivery_status(self, request, pk=None):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            logger.warning(f"Admin {request.user.username} tried to update non-existent order ID {pk}")
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = DeliveryStatusSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Admin {request.user.username} updated delivery status of order {pk}")
            return Response(serializer.data)
        logger.warning(f"Failed to update delivery status for order {pk}. Errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=CancelOrderSerializer,
        responses={200: openapi.Schema(type=openapi.TYPE_OBJECT, properties={'detail': openapi.Schema(type=openapi.TYPE_STRING)} )}
    )
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_order(self, request, pk=None):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            logger.warning(f"User {request.user.username} tried to cancel non-existent order ID {pk}")
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.is_staff and order.user != request.user:
            logger.warning(f"User {request.user.username} unauthorized to cancel order ID {pk}")
            return Response({"detail": "You are not allowed to cancel this order."}, status=status.HTTP_403_FORBIDDEN)

        serializer = CancelOrderSerializer(data=request.data)
        if serializer.is_valid():
            reason = serializer.validated_data.get('reason')
            order.order_status = 'cancelled'
            order.save()
            logger.info(f"Order {pk} cancelled by {request.user.username} for reason: {reason}")
            return Response({"detail": "Order cancelled successfully."})
        logger.warning(f"Failed to cancel order {pk}. Validation error: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)