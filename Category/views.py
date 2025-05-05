# views.py

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Category
from .serializers import CategorySerializer

class CategoryViewSet(viewsets.ModelViewSet):
    
    queryset = Category.objects.all()  # Retrieve all categories
    serializer_class = CategorySerializer  # Use CategorySerializer to format the response
    permission_classes = [IsAuthenticated]  # Default permission class: Only authenticated users can access

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get_permissions(self):
        
        if self.action in ['create', 'update', 'destroy']:
            return [IsAdminUser()]  # Only admin can modify the data (create, update, delete)
        return [IsAuthenticated()]  # Any authenticated user can view categories

    def create(self, request, *args, **kwargs):
        
        is_many = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)  # Save new category to the database
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        
        category = self.get_object()  # Get the category by ID
        serializer = self.get_serializer(category, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()  # Save updated data to the database
        return Response(serializer.data)  # Return updated category

    def destroy(self, request, *args, **kwargs):
        
        category = self.get_object()  # Get the category to delete
        category.delete()  # Delete category from the database
        return Response(status=status.HTTP_204_NO_CONTENT)  # Return success response
