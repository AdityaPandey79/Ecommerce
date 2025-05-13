# views.py

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Category
from .serializers import CategorySerializer

class CategoryViewSet(viewsets.ModelViewSet):
    
    queryset = Category.objects.all()  
    serializer_class = CategorySerializer  
    permission_classes = [IsAuthenticated] 

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get_permissions(self):
        
        if self.action in ['create', 'update', 'destroy']:
            return [IsAdminUser()]  
        return [IsAuthenticated()]  

    def create(self, request, *args, **kwargs):
        
        is_many = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)  
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        
        category = self.get_object()  # Get the category by ID
        serializer = self.get_serializer(category, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()  
        return Response(serializer.data)  

    def destroy(self, request, *args, **kwargs):
        
        category = self.get_object()  
        category.delete()  
        return Response(status=status.HTTP_204_NO_CONTENT) 