from django.urls import path
from . import views

urlpatterns = [
    path('place-order/', views.place_order, name='place_order'),
    path('my-orders/', views.user_orders, name='user_orders'),
    path('admin-orders/', views.admin_orders, name='admin_orders'),
    path('update-delivery-status/<int:pk>/', views.update_delivery_status, name='update_delivery_status'),
    path('orders/<int:pk>/cancel/', views.cancel_order),
]
