# product/views.py

import logging
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Product
from .serializers import ProductSerializer

# Initialize logger
logger = logging.getLogger(__name__)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Modify permissions based on action:
        - Admin can create, update, delete
        - Any authenticated user can retrieve (view) products
        """
        if self.action in ['create', 'update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()

    # POST
    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=is_many)

        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            logger.info(f"Product(s) created by {request.user.username}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.warning(f"Failed to create product(s). Error: {str(e)}")
            return Response({"error": "Failed to create product", "details": str(e)},
                            status=status.HTTP_400_BAD_REQUEST)

    # GET
    def retrieve(self, request, pk=None):
        try:
            product = self.get_object()
            logger.info(f"Product ID {product.id} viewed by {request.user.username}")
            serializer = self.get_serializer(product)
            return Response(serializer.data)
        except Exception as e:
            logger.warning(f"Failed to retrieve product. Error: {str(e)}")
            return Response({"error": "Product not found", "details": str(e)},
                            status=status.HTTP_404_NOT_FOUND)

    # PUT: Full update
    def update(self, request, pk=None):
        try:
            product = self.get_object()
            logger.info(f"User {request.user.username} is updating product ID {product.id}")
            serializer = self.get_serializer(product, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            logger.info(f"Product ID {product.id} updated by {request.user.username}")
            return Response(serializer.data)
        except Exception as e:
            logger.warning(f"Failed to update product ID {product.id}. Error: {str(e)}")
            return Response({"error": "Failed to update product", "details": str(e)},
                            status=status.HTTP_400_BAD_REQUEST)

    # DELETE
    def destroy(self, request, pk=None):
        try:
            product = self.get_object()
            logger.info(f"User {request.user.username} is deleting product ID {product.id}")
            product.delete()
            logger.info(f"Product ID {product.id} deleted by {request.user.username}")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Failed to delete product. Error: {str(e)}")
            return Response({"error": "Failed to delete product", "details": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)