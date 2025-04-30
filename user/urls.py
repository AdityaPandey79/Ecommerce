from django.urls import path
from .views import MyTokenObtainPairView, MyTokenRefreshView, UserView

urlpatterns = [
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', MyTokenRefreshView.as_view(), name='token_refresh'),
    path('user-view/', UserView.as_view(), name='user-view'),
]
