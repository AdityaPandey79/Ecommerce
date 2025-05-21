# order/views.py

import logging
from django.core.cache import cache  
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Order
from django.core.exceptions import ValidationError
from Product.models import Product
from .serializers import OrderSerializer, DeliveryStatusSerializer, CancelOrderSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from time import time  

# Initialize logger
logger = logging.getLogger(__name__)

class OrderViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    CACHE_KEY_USER_ORDERS = 'user_orders_{user_id}'  # Cache key for user-specific orders
    CACHE_KEY_ADMIN_ORDERS = 'admin_orders'         # Cache key for all orders
    CACHE_TIMEOUT = 3600  # Cache timeout: 1 hour

    @swagger_auto_schema(
        request_body=OrderSerializer,
        responses={201: OrderSerializer}
    )
    @action(detail=False, methods=['post'], url_path='place-order')
    def place_order(self, request):
        serializer = OrderSerializer(data=request.data)
        
        if serializer.is_valid():
            # Extract product and quantity from validated data
            product_id = serializer.validated_data.get('product').product_id
            quantity = serializer.validated_data.get('quantity')
            
            try:
                # Fetch the product
                product = Product.objects.get(product_id=product_id)
                
                # Validate stock availability
                if product.quantity < quantity:
                    logger.warning(f"Failed to place order. Insufficient stock for product ID {product_id}")
                    return Response(
                        {"error": f"Sorry, we only have {product.quantity} units of {product.name} in stock."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Deduct stock
                product.quantity -= quantity
                product.save()
                
                # Log low stock warning if necessary
                if product.quantity <= 10:
                    logger.warning(f"'{product.name}' is about to get out of stock. Current stock: {product.quantity}")
                
                # Save the order with the user
                serializer.save(user=request.user)
                logger.info(f"Order placed by {request.user.username}: {serializer.data}")

                # Invalidate the cache after placing an order
                cache.delete(self.CACHE_KEY_USER_ORDERS.format(user_id=request.user.id))
                cache.delete(self.CACHE_KEY_ADMIN_ORDERS)
                logger.info("Order cache invalidated after placing an order")
                
                return Response({"detail": "Order placed successfully!"}, status=status.HTTP_201_CREATED)
            
            except Product.DoesNotExist:
                logger.error(f"Product with ID {product_id} not found.")
                return Response(
                    {"error": "Product not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
            except ValidationError as e:
                logger.error(f"Validation error while placing order: {str(e)}")
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        logger.warning(f"Failed to place order. Errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        responses={200: OrderSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='my-orders')
    def user_orders(self, request):
        start_time = time()  # Record the start time

        try:
            # Check if the user's orders are cached
            cache_key = self.CACHE_KEY_USER_ORDERS.format(user_id=request.user.id)
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.info(f"{request.user.username}'s orders served from cache")
                response = Response(cached_data)
            else:
                # Fetch data from the database
                orders = Order.objects.filter(user=request.user)
                serializer = OrderSerializer(orders, many=True)
                data = serializer.data

                # Cache the data
                cache.set(cache_key, data, timeout=self.CACHE_TIMEOUT)
                logger.info(f"{request.user.username}'s orders fetched from DB and cached for {self.CACHE_TIMEOUT} seconds")
                response = Response(data)

            end_time = time()  # Record the end time
            logger.info(f"Response time: {end_time - start_time:.4f} seconds")  # Log the response time
            return response

        except Exception as e:
            logger.error(f"Failed to fetch user orders. Error: {str(e)}")
            return Response({"error": "Failed to fetch orders", "details": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        responses={200: OrderSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='admin-orders', permission_classes=[IsAdminUser])
    def admin_orders(self, request):
        start_time = time()  # Record the start time

        try:
            # Check if the admin's orders are cached
            cached_data = cache.get(self.CACHE_KEY_ADMIN_ORDERS)
            if cached_data:
                logger.info(f"Admin {request.user.username} fetched all orders from cache")
                response = Response(cached_data)
            else:
                # Fetch data from the database
                orders = Order.objects.all()
                serializer = OrderSerializer(orders, many=True)
                data = serializer.data

                # Cache the data
                cache.set(self.CACHE_KEY_ADMIN_ORDERS, data, timeout=self.CACHE_TIMEOUT)
                logger.info(f"Admin {request.user.username} fetched all orders from DB and cached for {self.CACHE_TIMEOUT} seconds")
                response = Response(data)

            end_time = time()  # Record the end time
            logger.info(f"Response time: {end_time - start_time:.4f} seconds")  # Log the response time
            return response

        except Exception as e:
            logger.error(f"Failed to fetch admin orders. Error: {str(e)}")
            return Response({"error": "Failed to fetch orders", "details": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

            # Invalidate the cache after updating delivery status
            cache.delete(self.CACHE_KEY_ADMIN_ORDERS)
            cache.delete(self.CACHE_KEY_USER_ORDERS.format(user_id=order.user.id))
            logger.info("Order cache invalidated after updating delivery status")

            return Response(serializer.data)
        logger.warning(f"Failed to update delivery status for order {pk}. Errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=CancelOrderSerializer,
        responses={200: openapi.Schema(type=openapi.TYPE_OBJECT, properties={'detail': openapi.Schema(type=openapi.TYPE_STRING)})}
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
            order.cancel_order()
            order.order_status = 'cancelled'
            order.save()
            product = order.product
            logger.info(
                f"Order {pk} cancelled by {request.user.username} for reason: {reason}. "
                f"Updated stock for product '{product.name}' (ID: {product.product_id}): {product.quantity}"
            )

            # Invalidate the cache after canceling an order
            cache.delete(self.CACHE_KEY_ADMIN_ORDERS)
            cache.delete(self.CACHE_KEY_USER_ORDERS.format(user_id=order.user.id))
            logger.info("Order cache invalidated after canceling an order")

            return Response({"detail": "Order cancelled successfully."})
        logger.warning(f"Failed to cancel order {pk}. Validation error: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)