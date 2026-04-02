from django.urls import path
from .views import register, verify_email, request_password_reset, confirm_password_reset
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify-email/', verify_email, name='verify_email'),
    path('request-password-reset/', request_password_reset, name='request_password_reset'),
    path('confirm-password-reset/', confirm_password_reset, name='confirm_password_reset'),
]