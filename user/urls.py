from django.urls import path, include
from rest_framework.routers import DefaultRouter
from user.views import MyTokenObtainPairView, MyTokenRefreshView, UserViewSet

# Set up the router
router = DefaultRouter()
router.register('users', UserViewSet, basename='user')  # Register the UserViewSet

urlpatterns = [
    path('login/', MyTokenObtainPairView.as_view(), name='user_login_token'),
    path('token/refresh/', MyTokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),  # Includes the URLs for the viewset
]
