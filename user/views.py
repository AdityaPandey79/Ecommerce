from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from django.contrib.auth.models import User
from user.serializers import UserSerializer
from Category.models import Category
from Category.serializers import CategorySerializer

# View to get JWT token
class MyTokenObtainPairView(TokenObtainPairView):
    pass  # You can customize token claims later if needed

# View to refresh JWT token
class MyTokenRefreshView(TokenRefreshView):
    pass

# View that only admin can access (to manage users)
class UserView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]  # Only admins can access

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')  # optional parameter
        if user_id:
            user = get_object_or_404(User, pk=user_id)
            serializer = UserSerializer(user)
        else:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
