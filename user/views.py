# user/views.py

import logging
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.signals import user_logged_in
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from user.serializers import UserSerializer

# Initialize logger
logger = logging.getLogger(__name__)


class MyTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            logger.warning(f"Login failed for user {request.data.get('username')}: Invalid credentials")
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        user = serializer.user
        if user:
            user_logged_in.send(sender=user.__class__, request=request, user=user)
            logger.info(f"User {user.username} logged in successfully")

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class MyTokenRefreshView(TokenRefreshView):
    pass


# User ViewSet - handles list, retrieve, create, update, delete
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            logger.info(f"User created: {serializer.validated_data['username']} (by {request.user.username})")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.warning(f"Failed to create user. Error: {str(e)}")
            return Response({"error": "User creation failed", "details": str(e)},
                            status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            logger.info(f"User {instance.username} updated by {request.user.username}")
            return Response(serializer.data)
        except Exception as e:
            logger.warning(f"Failed to update user {instance.username}. Error: {str(e)}")
            return Response({"error": "User update failed", "details": str(e)},
                            status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        username = instance.username
        try:
            self.perform_destroy(instance)
            logger.info(f"User {username} deleted by {request.user.username}")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Failed to delete user {username}. Error: {str(e)}")
            return Response({"error": "User deletion failed", "details": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)