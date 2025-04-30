# views.py

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Category
from .serializers import CategorySerializer

class CategoryViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides the standard actions for Category model.
    - Admin can create, update, partial_update, delete.
    - Authenticated users can list and retrieve categories.
    """
    
    queryset = Category.objects.all()  # Retrieve all categories
    serializer_class = CategorySerializer  # Use CategorySerializer to format the response
    permission_classes = [IsAuthenticated]  # Default permission class: Only authenticated users can access

    def get_permissions(self):
        """
        Customize permissions:
        - Admins can create, update, delete
        - Authenticated users can list and retrieve
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]  # Only admin can modify the data (create, update, delete)
        return [IsAuthenticated()]  # Any authenticated user can view categories

    def create(self, request, *args, **kwargs):
        """
        Handle creation of new categories.
        This method is customized for bulk category creation if needed.
        """
        is_many = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)  # Save new category to the database
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Handle full update of an existing category.
        Only admins are allowed to do this.
        """
        category = self.get_object()  # Get the category by ID
        serializer = self.get_serializer(category, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()  # Save updated data to the database
        return Response(serializer.data)  # Return updated category

    def destroy(self, request, *args, **kwargs):
        """
        Handle deletion of a category.
        Only admins are allowed to delete a category.
        """
        category = self.get_object()  # Get the category to delete
        category.delete()  # Delete category from the database
        return Response(status=status.HTTP_204_NO_CONTENT)  # Return success response
