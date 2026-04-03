from rest_framework.decorators import api_view, throttle_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from .serializers import RegisterSerializer, UserSerializer
from .models import User
from .permissions import IsAdmin

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users. Accessible only by Admins.
    Allows listing, updating roles, and managing active status.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    http_method_names = ['get', 'put', 'patch', 'delete'] # Registration is handled separately

@api_view(['POST'])
@throttle_classes([AnonRateThrottle])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    
    # Send verification email
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    
    # Note: Using absolute URI for verification
    verify_url = request.build_absolute_uri(f"/api/auth/verify-email/?uid={uidb64}&token={token}")
    
    send_mail(
        subject="Verify your email",
        message=f"Please verify your email by clicking the following link: {verify_url}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    
    return Response({"message": "User created. Please check your email to verify your account."}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def verify_email(request):
    uidb64 = request.GET.get('uid')
    token = request.GET.get('token')
    
    if not uidb64 or not token:
        return Response({"error": "Missing uid or token"}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return Response({"message": "Email verified successfully. You can now log in."})
    else:
        return Response({"error": "Invalid verification link"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@throttle_classes([AnonRateThrottle])
def request_password_reset(request):
    username = request.data.get('username')
    try:
        user = User.objects.get(username=username)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = request.build_absolute_uri(f"/api/auth/confirm-password-reset/?uid={uidb64}&token={token}")
        
        send_mail(
            "Password Reset",
            f"Reset your password using this link: {reset_url}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )
    except User.DoesNotExist:
        pass
        
    return Response({"message": "If the user exists, a password reset email has been sent."})

@api_view(['POST'])
@throttle_classes([AnonRateThrottle])
def confirm_password_reset(request):
    uidb64 = request.data.get('uid')
    token = request.data.get('token')
    new_password = request.data.get('new_password')
    
    if not all([uidb64, token, new_password]):
        return Response({"error": "uid, token, and new_password are required"}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({"error": "Invalid reset link"}, status=status.HTTP_400_BAD_REQUEST)

    if default_token_generator.check_token(user, token):
        user.set_password(new_password)
        user.save()
        return Response({"message": "Password has been reset successfully."})
    else:
        return Response({"error": "Invalid or expired reset link"}, status=status.HTTP_400_BAD_REQUEST)
