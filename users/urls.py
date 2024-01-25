# urls.py
from django.urls import path,re_path,include
from .views import CustomTokenObtainPairView,UserViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,TokenVerifyView
)
from rest_framework.routers import DefaultRouter
router = DefaultRouter()


router.register('', UserViewSet,basename="registration")
urlpatterns = [
    re_path(r'^token/$', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('', include(router.urls)),


]
