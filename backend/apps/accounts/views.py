import re

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, logout
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.db import IntegrityError

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .authentication import CookieJWTAuthentication
from .models import NewsletterSubscriber
from .serializers import SignupSerializer, NewsletterSubscribeSerializer, ProfileSerializer
from .utils import mask_phone, normalize_phone
from .twilio_verify import send_verification_code, check_verification_code

from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.conf import settings

# Create your views here.

User = get_user_model()

# --------------- Login --------------- #
@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get("username", "").strip()
    password = request.data.get("password", "")

    if not username or not password:
        return Response(
            {"error": "Username and password are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    user = authenticate(request=request, username=username, password=password)

    if user is None:
        return Response(
            {
                "success": False,
                "error": "Invalid username or password. Please try again."
            },
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    response = Response(
        {
            "success": True,
            "message": "Login successful",
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "role": getattr(user, "role", "user"),
            },
        },
        status=status.HTTP_200_OK,
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
        max_age=60 * 60,
        path="/",
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
        max_age=60 * 60 * 24 * 7,
        path="/",
    )

    return response

# --------------- Signup --------------- #
@api_view(["POST"])
@permission_classes([AllowAny])
def signup(request):
    try:
        serializer = SignupSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
    
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response(
            {
                "success": True,
                "message": "Account created successfully",
                "user": {
                    "id": user.id,
                    "first_name": user.first_name,
                    "email": user.email,
                    "role": getattr(user, "role", "user"),
                },
            },
            status=status.HTTP_201_CREATED,
        )

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax",
            max_age=60 * 60,
            path="/",
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax",
            max_age=60 * 60 * 24 * 7,
            path="/",
        )

        return response
    except Exception as e:
        return Response(
            {
                "success": False,
                "error": "Something went wrong. Please try again."
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

# -------------- User -------------- #
@api_view(["GET"])
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAuthenticated])
def user_me(request):
    user = request.user

    return Response(
        {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "phone": user.phone,
            "alternate_phone": user.alternate_phone,
            "gender": user.gender,
            "address_line_1": user.address_line_1,
            "address_line_2": user.address_line_2,
            "city": user.city,
            "state": user.state,
            "pincode": user.pincode,
            "country": user.country,
            "role": getattr(user, "role", "user"),
        },
        status=status.HTTP_200_OK,
    )

# --------------- Profile -------------- #
@api_view(["GET"])
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAuthenticated])
def profile(request):
    serializer = ProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)

# --------------- Update Profile --------------- #
@api_view(["PUT", "PATCH"])
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAuthenticated])
def update_profile(request):
    data = request.data.copy()

    for field in ["phone", "alternate_phone"]:
        if data.get(field) == "":
            data[field] = None
    serializer = ProfileSerializer(
        request.user,
        data=data,
        partial=True
    )

    if not serializer.is_valid():
        # serializer.save()
        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    try:
        serializer.save()

        return Response(
            {
                "success": True,
                "message": "Profile updated successfully",
                "user": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    except IntegrityError:
        return Response(
            {
                "success": False,
                "message": "Phone number or alternate phone number already exists.",
                "errors": {
                    "phone": ["Phone number must be unique."],
                    "alternate_phone": ["Alternate phone number must be unique."],
                },
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        return Response(
            {
                "success": False,
                "message": str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

# --------------- Password reset OTP --------------- #
def get_user_by_phone(phone_number: str):
    return User.objects.filter(phone=phone_number).first()

# --------------- Send OTP --------------- #
@api_view(["POST"])
@permission_classes([AllowAny])
def send_forgot_password_otp(request):
    try:
        raw_phone = request.data.get("phoneNumber", "")
        phone_number = normalize_phone(raw_phone)

        user = get_user_by_phone(phone_number)
        if not user:
            return Response(
                {"error": "No account found with this mobile number."},
                status=404
            )
        success, result = send_verification_code(phone_number)

        if not success:
            return Response(
                {"error": result.get("error", "Failed to send OTP.")},
                status=500
            )
        
        expiry_seconds = 30 * 60  # 30 minutes

        return Response(
            {
                "message": "OTP sent successfully.",
                "phoneNumber": phone_number,
                "maskedPhone": mask_phone(phone_number),
                "status": result.get("status"),
                "expiresIn": expiry_seconds,
            },
            status=200
        )
    except ValueError as exc:
        return Response({"error": str(exc)}, status=400)
    except Exception as exc:
        return Response({"error": "Something went wrong. Please try again."}, status=500)

# --------------- Resend Password --------------- #
@api_view(["POST"])
@permission_classes([AllowAny])
def resend_forgot_password_otp(request):
    try:
        raw_phone = request.data.get("phoneNumber", "")
        phone_number = normalize_phone(raw_phone)

        user = get_user_by_phone(phone_number)
        if not user:
            return Response(
                {"error": "No account found with this mobile number."},
                status=404
            )
        
        success, result = send_verification_code(phone_number)

        if not success:
            return Response(
                {"error": result.get("error", "Failed to resend OTP.")},
                status=500
            )
        
        return Response(
            {
                "message": "OTP resent successfully.",
                "phoneNumber": phone_number,
                "maskedPhone": mask_phone(phone_number),
                "status": result.get("status"),
            },
            status=200
        )

    except ValueError as exc:
        return Response({"error": str(exc)}, status=400)
    except Exception as exc:
        return Response({"error": "Something went wrong. Please try again."}, status=500)

# --------------- Verify OTP --------------- #
@api_view(["POST"])
@permission_classes([AllowAny])
def verify_forgot_password_otp(request):
    try:
        raw_phone = request.data.get("phoneNumber", "")
        otp = (request.data.get("otp", "") or "").strip()

        phone_number = normalize_phone(raw_phone)

        if not re.fullmatch(r"^\d{4,10}$", otp):
            return Response(
                {"error": "Please enter a valid OTP."},
                status=400
            )
        
        success, result = check_verification_code(phone_number, otp)

        if not success:
            return Response(
                {"error": result.get("error", "OTP verification failed.")},
                status=500
            )
        
        if not result.get("valid"):
            return Response(
                {"error": "Invalid or expired OTP."},
                status=400
            )
        
        cache_key = f"pwd_reset_verified:{phone_number}"
        cache.set(cache_key, True, timeout=10 * 60)

        return Response(
            {
                "message": "OTP verified successfully.",
                "phoneNumber": phone_number,
            },
            status=200
        )
    
    except ValueError as exc:
        return Response({"error": str(exc)}, status=400)
    except Exception as exc:
        return Response({"error": "Something went wrong. Please try again."}, status=500)

# --------------- Reset Password --------------- #
@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password_with_otp(request):
    try:
        raw_phone = request.data.get("phoneNumber", "")
        new_password = (request.data.get("newPassword", "") or "").strip()
        confirm_password = (request.data.get("confirmPassword", "") or "").strip()

        phone_number = normalize_phone(raw_phone)

        if not new_password or len(new_password) < 8:
            return Response(
                {"error": "Password must be at least 8 characters long."},
                status=400
            )
        
        if new_password != confirm_password:
            return Response(
                {"error": "Passwords do not match."},
                status=400
            )
        
        cache_key = f"pwd_reset_verified:{phone_number}"
        is_verified = cache.get(cache_key)

        if not is_verified:
            return Response(
                {"error": "OTP verification required before resetting password."},
                status=403
            )
        
        user = get_user_by_phone(phone_number)
        if not user:
            return Response(
                {"error": "No account found with this mobile number."},
                status=404
            )
        
        validate_password(new_password, user=user)

        user.set_password(new_password)
        user.save()

        cache.delete(cache_key)

        return Response(
            {"message": "Password reset successfully."},
            status=200
        )
    
    except ValueError as exc:
        return Response({"error": str(exc)}, status=400)
    except Exception as exc:
        return Response({"error": "Something went wrong. Please try again."}, status=500)

# --------------- Logout --------------- #
@api_view(["POST"])
@permission_classes([AllowAny])
def logout_view(request):
    refresh_token = request.COOKIES.get("refresh_token")

    if refresh_token:
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            pass
        except Exception:
            pass

    response = Response(
        {"message": "Logout successful"},
        status=status.HTTP_200_OK,
    )

    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")

    return response

class AdminPasswordChangeView(PasswordChangeView):
    template_name = "registration/password_change_form.html"

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "Password changed successfully. Please login again."
        )

        logout(self.request)

        return response
    
    def get_success_url(self):
        return reverse_lazy("admin:login")

# --------------- Session --------------- #
@api_view(["GET"])
@authentication_classes([CookieJWTAuthentication])
@permission_classes([AllowAny])
def session_status(request):
    if request.user and request.user.is_authenticated:
        return Response(
            {
                "authenticated": True,
                "user": {
                    "id": request.user.id,
                    "first_name": request.user.first_name,
                    "email": request.user.email,
                    "phone": request.user.phone,
                    "alternate_phone": request.user.alternate_phone,
                    "gender": request.user.gender,
                    "address_line_1": request.user.address_line_1,
                    "address_line_2": request.user.address_line_2,
                    "city": request.user.city,
                    "state": request.user.state,
                    "pincode": request.user.pincode,
                    "country": request.user.country,
                    "role": getattr(request.user, "role", "user"),
                },
            },
            status=status.HTTP_200_OK,
        )

    return Response(
        {
            "authenticated": False,
            "user": None,
        },
        status=status.HTTP_200_OK,
    )

# --------------- Newsletter --------------- #
@api_view(["POST"])
@permission_classes([AllowAny])
def subscribe_newsletter(request):
    serializer = NewsletterSubscribeSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {
                "success": False,
                "message": "Please enter a valid email address.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    email = serializer.validated_data["email"]

    subscriber, created = NewsletterSubscriber.objects.get_or_create(
        email=email,
        defaults={"is_active": True},
    )

    if created:
        return Response(
            {
                "success": True,
                "message": "You have subscribed successfully.",
                "data": {
                    "email": subscriber.email,
                    "is_active": subscriber.is_active,
                },
            },
            status=status.HTTP_201_CREATED,
        )
    
    if not subscriber.is_active:
        subscriber.is_active = True
        subscriber.save(update_fields=["is_active", "updated_at"])

        return Response(
            {
                "success": True,
                "message": "Your newsletter subscription has been reactivated.",
                "data": {
                    "email": subscriber.email,
                    "is_active": subscriber.is_active,
                },
            },
            status=status.HTTP_200_OK,
        )
    
    return Response(
        {
            "success": False,
            "message": "This email is already subscribed.",
        },
        status=status.HTTP_409_CONFLICT,
    )