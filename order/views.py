from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models import Order
from .serializers import OrderSerializer, DeliveryStatusSerializer,CancelOrderSerializer

# API to place an order
@swagger_auto_schema(
    method='post',
    request_body=OrderSerializer,
    responses={
        201: openapi.Response("Order placed successfully", OrderSerializer),
        400: "Bad request"
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_order(request):
    serializer = OrderSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)  # Associate the order with the logged-in user
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# API for users to see their orders
@swagger_auto_schema(
    method='get',
    responses={200: openapi.Response("List of user's orders", OrderSerializer(many=True))}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_orders(request):
    orders = Order.objects.filter(user=request.user)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

# Admin API to see all orders
@swagger_auto_schema(
    method='get',
    responses={200: openapi.Response("List of all orders", OrderSerializer(many=True))}
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_orders(request):
    orders = Order.objects.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

# API to update the delivery status
@swagger_auto_schema(
    method='patch',
    request_body=DeliveryStatusSerializer,
    responses={
        200: openapi.Response("Delivery status updated", DeliveryStatusSerializer),
        400: "Bad request",
        404: "Order not found"
    }
)
@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def update_delivery_status(request, pk):
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
    method='delete',
    request_body=CancelOrderSerializer,
    responses={
        200: "Order cancelled successfully",
        403: "Not allowed to cancel this order",
        404: "Order not found",
        400: "Bad request"
    }
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cancel_order(request, pk):
    try:
        order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

    # Check permission
    if not request.user.is_staff and order.user != request.user:
        return Response({"detail": "You are not allowed to cancel this order."}, status=status.HTTP_403_FORBIDDEN)

    # Validate reason from request body
    serializer = CancelOrderSerializer(data=request.data)
    if serializer.is_valid():
        reason = serializer.validated_data.get('reason')
        # You can log the reason or store it somewhere if required.
        print(f"Order {pk} cancelled by {request.user.username} for reason: {reason}")
        order.delete()
        return Response({"detail": "Order cancelled successfully."})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
