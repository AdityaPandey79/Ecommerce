# category/views.py

import logging
from django.core.cache import cache 
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Category
from .serializers import CategorySerializer
from time import time  

# Initialize logger
logger = logging.getLogger(__name__)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    CACHE_KEY_CATEGORY_LIST = 'category_list'  # Cache key for category list
    CACHE_TIMEOUT = 3600  # Cache timeout: 1 hour

    def perform_create(self, serializer):
        user = self.request.user
        logger.info(f"User {user.username} is creating a new category")
        serializer.save(created_by=user, updated_by=user)
        logger.info(f"Category created by {user.username}")

        # Invalidate the cache after creation
        cache.delete(self.CACHE_KEY_CATEGORY_LIST)
        logger.info("Category list cache invalidated after creation")

    def perform_update(self, serializer):
        user = self.request.user
        category = self.get_object()
        logger.info(f"User {user.username} is updating category ID {category.id}")
        serializer.save(updated_by=self.request.user)
        logger.info(f"Category ID {category.id} updated by {user.username}")

        # Invalidate the cache after update
        cache.delete(self.CACHE_KEY_CATEGORY_LIST)
        logger.info("Category list cache invalidated after update")

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

            # Invalidate the cache after deletion
            cache.delete(self.CACHE_KEY_CATEGORY_LIST)
            logger.info("Category list cache invalidated after deletion")

            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Failed to delete category ID {category_id}. Error: {str(e)}")
            return Response({"error": "Failed to delete category", "details": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request, *args, **kwargs):
        start_time = time()  # Record the start time

        try:
            # Check if the category list is cached
            cached_data = cache.get(self.CACHE_KEY_CATEGORY_LIST)
            if cached_data:
                logger.info(f"Category list served from cache to {request.user.username}")
                response = Response(cached_data)
            else:
                # Fetch data from the database
                queryset = self.get_queryset()
                serializer = self.get_serializer(queryset, many=True)
                data = serializer.data

                # Cache the data
                cache.set(self.CACHE_KEY_CATEGORY_LIST, data, timeout=self.CACHE_TIMEOUT)
                logger.info(f"Category list fetched from DB and cached for {self.CACHE_TIMEOUT} seconds")
                response = Response(data)

            end_time = time()  # Record the end time
            logger.info(f"Response time: {end_time - start_time:.4f} seconds")  # Log the response time
            return response

        except Exception as e:
            logger.error(f"Failed to list categories. Error: {str(e)}")
            return Response({"error": "Failed to fetch categories", "details": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)