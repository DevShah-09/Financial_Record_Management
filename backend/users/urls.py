from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    register, verify_email, request_password_reset, confirm_password_reset,
    UserViewSet
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', register, name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify-email/', verify_email, name='verify_email'),
    path('request-password-reset/', request_password_reset, name='request_password_reset'),
    path('confirm-password-reset/', confirm_password_reset, name='confirm_password_reset'),
]