from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.signals import user_logged_in
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from user.serializers import UserSerializer


class MyTokenObtainPairView(TokenObtainPairView):
    #pass

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        user = serializer.user

        if user:
            user_logged_in.send(sender=user.__class__, request=request, user=user)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class MyTokenRefreshView(TokenRefreshView):
    pass


# User ViewSet - handles list, retrieve, create, update, delete
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]