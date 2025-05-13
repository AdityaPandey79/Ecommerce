from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Order
from .serializers import OrderSerializer, DeliveryStatusSerializer, CancelOrderSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


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
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        responses={200: OrderSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='my-orders')
    def user_orders(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        responses={200: OrderSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='admin-orders', permission_classes=[IsAdminUser])
    def admin_orders(self, request):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
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
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = DeliveryStatusSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
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
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.is_staff and order.user != request.user:
            return Response({"detail": "You are not allowed to cancel this order."}, status=status.HTTP_403_FORBIDDEN)

        serializer = CancelOrderSerializer(data=request.data)
        if serializer.is_valid():
            reason = serializer.validated_data.get('reason')
            print(f"Order {pk} cancelled by {request.user.username} for reason: {reason}")
            order.order_status = 'cancelled'
            order.save()
            return Response({"detail": "Order cancelled successfully."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)