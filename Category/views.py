# category/views.py

import logging
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Category
from .serializers import CategorySerializer

# Initialize logger
logger = logging.getLogger(__name__)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        logger.info(f"User {user.username} is creating a new category")
        serializer.save(created_by=user, updated_by=user)
        logger.info(f"Category created by {user.username}")

    def perform_update(self, serializer):
        user = self.request.user
        category = self.get_object()
        logger.info(f"User {user.username} is updating category ID {category.id}")
        serializer.save(updated_by=self.request.user)
        logger.info(f"Category ID {category.id} updated by {user.username}")

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=is_many)

        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.warning(f"Failed to create category. Error: {str(e)}")
            return Response({"error": "Failed to create category", "details": str(e)},
                            status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        category = self.get_object()  # Get the category by ID
        serializer = self.get_serializer(category, data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except Exception as e:
            logger.warning(f"Failed to update category ID {category.id}. Error: {str(e)}")
            return Response({"error": "Failed to update category", "details": str(e)},
                            status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        category = self.get_object()
        category_id = category.id
        try:
            category.delete()
            logger.info(f"Category ID {category_id} deleted by user {request.user.username}")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Failed to delete category ID {category_id}. Error: {str(e)}")
            return Response({"error": "Failed to delete category", "details": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)