from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RestaurantViewSet,
    MenuViewSet,
    MenuItemViewSet,
    OrderViewSet,
    PaymentViewSet
)

router = DefaultRouter()
router.register(r'restaurants_info', RestaurantViewSet, basename='restaurant')
router.register(r'menus', MenuViewSet, basename='menu')
router.register(r'items', MenuItemViewSet, basename='item')
router.register(r'orders', OrderViewSet,basename="orders")
router.register(r'payments', PaymentViewSet) # there will (payable) and (pay_stripe)

urlpatterns = [
    path('', include(router.urls)),
]
