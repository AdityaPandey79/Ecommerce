from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet

# Create a router and register your viewset
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')

# Include the router URLs in the urlpatterns
urlpatterns = [
    path('', include(router.urls)),
]
