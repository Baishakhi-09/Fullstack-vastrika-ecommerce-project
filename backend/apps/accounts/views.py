from __future__ import annotations

import logging
import re
from typing import Any

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    get_user_model,
    logout,
)
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.password_validation import (
    validate_password,
)
from django.contrib.auth.views import (
    PasswordChangeView,
)
from django.core.cache import cache
from django.db import IntegrityError, transaction
from django.urls import reverse_lazy

from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.request import Request
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import (
    RefreshToken,
    TokenError,
)

from .authentication import CookieJWTAuthentication
from .models import NewsletterSubscriber
from .serializers import (
    NewsletterSubscribeSerializer,
    ProfileSerializer,
    SignupSerializer,
)
from .twilio_verify import (
    check_verification_code,
    send_verification_code,
)
from .utils import (
    mask_phone,
    normalize_phone,
)

logger = logging.getLogger(__name__)

User = get_user_model()


# =========================================================
# CONSTANTS
# =========================================================
ACCESS_TOKEN_COOKIE = "access_token"
REFRESH_TOKEN_COOKIE = "refresh_token"

ACCESS_TOKEN_MAX_AGE = 60 * 60
REFRESH_TOKEN_MAX_AGE = 60 * 60 * 24 * 7

OTP_CACHE_TIMEOUT = 10 * 60
OTP_EXPIRY_SECONDS = 30 * 60

OTP_REGEX = re.compile(r"^\d{4,10}$")


# =========================================================
# RESPONSE HELPERS
# =========================================================
def success_response(
    *,
    message: str,
    data: dict[str, Any] | None = None,
    status_code: int = status.HTTP_200_OK,
) -> Response:
    """
    Standardized success response.
    """

    payload: dict[str, Any] = {
        "success": True,
        "message": message,
    }

    if data:
        payload.update(data)

    return Response(
        payload,
        status=status_code,
    )


def error_response(
    *,
    message: str,
    errors: dict[str, Any] | None = None,
    status_code: int = status.HTTP_400_BAD_REQUEST,
) -> Response:
    """
    Standardized error response.
    """

    payload: dict[str, Any] = {
        "success": False,
        "message": message,
    }

    if errors:
        payload["errors"] = errors

    return Response(
        payload,
        status=status_code,
    )


# =========================================================
# USER HELPERS
# =========================================================
def build_user_payload(
    user: AbstractBaseUser,
) -> dict[str, Any]:
    """
    Build reusable user payload.
    """

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "phone": getattr(user, "phone", None),
        "alternate_phone": getattr(user, "alternate_phone", None),
        "gender": getattr(user, "gender", None),
        "address_line_1": getattr(user, "address_line_1", None),
        "address_line_2": getattr(user, "address_line_2", None),
        "city": getattr(user, "city", None),
        "state": getattr(user, "state", None),
        "pincode": getattr(user, "pincode", None),
        "country": getattr(user, "country", None),
        "role": getattr(user, "role", "user"),
    }


def set_auth_cookies(
    *,
    response: Response,
    access_token: str,
    refresh_token: str,
) -> None:
    """
    Set JWT cookies.
    """

    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE,
        value=access_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
        max_age=ACCESS_TOKEN_MAX_AGE,
        path="/",
    )

    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE,
        value=refresh_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
        max_age=REFRESH_TOKEN_MAX_AGE,
        path="/",
    )


def clear_auth_cookies(
    response: Response,
) -> None:
    """
    Clear JWT cookies.
    """

    response.delete_cookie(
        ACCESS_TOKEN_COOKIE,
        path="/",
    )

    response.delete_cookie(
        REFRESH_TOKEN_COOKIE,
        path="/",
    )


def get_user_by_phone(
    phone_number: str,
) -> AbstractBaseUser | None:
    """
    Fetch user by phone number.
    """

    return User.objects.filter(
        phone=phone_number,
    ).first()


# =========================================================
# AUTHENTICATION
# =========================================================
@api_view(["POST"])
@permission_classes([AllowAny])
def signup(
    request: Request,
) -> Response:
    """
    Register new user.
    """

    serializer = SignupSerializer(
        data=request.data,
    )

    if not serializer.is_valid():

        return error_response(
            message="Signup validation failed.",
            errors=serializer.errors,
        )

    user = serializer.save()

    refresh = RefreshToken.for_user(user)

    response = success_response(
        message="Account created successfully.",
        data={
            "user": build_user_payload(user),
        },
        status_code=status.HTTP_201_CREATED,
    )

    set_auth_cookies(
        response=response,
        access_token=str(refresh.access_token),
        refresh_token=str(refresh),
    )

    logger.info(
        "New account created for '%s'.",
        user.username,
    )

    return response


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(
    request: Request,
) -> Response:
    """
    Authenticate user.
    """

    username = str(
        request.data.get("username", "")
    ).strip()

    password = str(
        request.data.get("password", "")
    )

    if not username or not password:

        return error_response(
            message="Username and password are required.",
        )

    user = authenticate(
        request=request,
        username=username,
        password=password,
    )

    if not user:

        logger.warning(
            "Failed login attempt for '%s'.",
            username,
        )

        return error_response(
            message="Invalid credentials.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    refresh = RefreshToken.for_user(user)

    response = success_response(
        message="Login successful.",
        data={
            "user": build_user_payload(user),
        },
    )

    set_auth_cookies(
        response=response,
        access_token=str(refresh.access_token),
        refresh_token=str(refresh),
    )

    return response


@api_view(["POST"])
@permission_classes([AllowAny])
def logout_view(
    request: Request,
) -> Response:
    """
    Logout user.
    """

    refresh_token = request.COOKIES.get(
        REFRESH_TOKEN_COOKIE,
    )

    if refresh_token:

        try:
            RefreshToken(refresh_token).blacklist()

        except TokenError:

            logger.warning(
                "Invalid refresh token during logout."
            )

    response = success_response(
        message="Logout successful.",
    )

    clear_auth_cookies(response)

    return response


# =========================================================
# SESSION
# =========================================================
@api_view(["GET"])
@authentication_classes([
    CookieJWTAuthentication,
])
@permission_classes([AllowAny])
def session_status(
    request: Request,
) -> Response:
    """
    Return session status.
    """

    if request.user and request.user.is_authenticated:

        return success_response(
            message="Authenticated session.",
            data={
                "authenticated": True,
                "user": build_user_payload(
                    request.user,
                ),
            },
        )

    return success_response(
        message="Anonymous session.",
        data={
            "authenticated": False,
            "user": None,
        },
    )


# =========================================================
# USER
# =========================================================
@api_view(["GET"])
@authentication_classes([
    CookieJWTAuthentication,
])
@permission_classes([
    IsAuthenticated,
])
def user_me(
    request: Request,
) -> Response:
    """
    Return authenticated user.
    """

    return success_response(
        message="User profile fetched successfully.",
        data={
            "user": build_user_payload(
                request.user,
            ),
        },
    )


@api_view(["GET"])
@authentication_classes([
    CookieJWTAuthentication,
])
@permission_classes([
    IsAuthenticated,
])
def profile(
    request: Request,
) -> Response:
    """
    Get profile.
    """

    serializer = ProfileSerializer(
        request.user,
    )

    return success_response(
        message="Profile fetched successfully.",
        data={
            "user": serializer.data,
        },
    )


@api_view(["PUT", "PATCH"])
@authentication_classes([
    CookieJWTAuthentication,
])
@permission_classes([
    IsAuthenticated,
])
def update_profile(
    request: Request,
) -> Response:
    """
    Update profile.
    """

    serializer = ProfileSerializer(
        request.user,
        data=request.data,
        partial=True,
    )

    if not serializer.is_valid():

        return error_response(
            message="Profile validation failed.",
            errors=serializer.errors,
        )

    try:

        serializer.save()

        return success_response(
            message="Profile updated successfully.",
            data={
                "user": serializer.data,
            },
        )

    except IntegrityError:

        return error_response(
            message="Phone number already exists.",
        )


# =========================================================
# OTP
# =========================================================
@api_view(["POST"])
@permission_classes([AllowAny])
def send_forgot_password_otp(
    request: Request,
) -> Response:
    """
    Send OTP.
    """

    try:

        raw_phone = request.data.get(
            "phoneNumber",
            "",
        )

        phone_number = normalize_phone(
            raw_phone,
        )

        user = get_user_by_phone(
            phone_number,
        )

        if not user:

            return error_response(
                message="Unable to process request.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        success, result = send_verification_code(
            phone_number,
        )

        if not success:

            return error_response(
                message=result.get(
                    "error",
                    "Failed to send OTP.",
                ),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return success_response(
            message="OTP sent successfully.",
            data={
                "phoneNumber": phone_number,
                "maskedPhone": mask_phone(phone_number),
                "expiresIn": OTP_EXPIRY_SECONDS,
            },
        )

    except ValueError as exc:

        return error_response(
            message=str(exc),
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def resend_forgot_password_otp(
    request: Request,
) -> Response:
    """
    Resend OTP.
    """

    return send_forgot_password_otp(request)


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_forgot_password_otp(
    request: Request,
) -> Response:
    """
    Verify OTP.
    """

    try:

        raw_phone = request.data.get(
            "phoneNumber",
            "",
        )

        otp = str(
            request.data.get("otp", "")
        ).strip()

        if not OTP_REGEX.fullmatch(otp):

            return error_response(
                message="Invalid OTP format.",
            )

        phone_number = normalize_phone(
            raw_phone,
        )

        success, result = check_verification_code(
            phone_number,
            otp,
        )

        if not success:

            return error_response(
                message=result.get(
                    "error",
                    "OTP verification failed.",
                ),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if not result.get("valid"):

            return error_response(
                message="Invalid or expired OTP.",
            )

        cache.set(
            f"pwd_reset_verified:{phone_number}",
            True,
            timeout=OTP_CACHE_TIMEOUT,
        )

        return success_response(
            message="OTP verified successfully.",
        )

    except ValueError as exc:

        return error_response(
            message=str(exc),
        )


@api_view(["POST"])
@permission_classes([AllowAny])
@transaction.atomic
def reset_password_with_otp(
    request: Request,
) -> Response:
    """
    Reset password.
    """

    try:

        phone_number = normalize_phone(
            request.data.get(
                "phoneNumber",
                "",
            )
        )

        new_password = str(
            request.data.get(
                "newPassword",
                "",
            )
        ).strip()

        confirm_password = str(
            request.data.get(
                "confirmPassword",
                "",
            )
        ).strip()

        if new_password != confirm_password:

            return error_response(
                message="Passwords do not match.",
            )

        verified = cache.get(
            f"pwd_reset_verified:{phone_number}"
        )

        if not verified:

            return error_response(
                message="OTP verification required.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        user = get_user_by_phone(
            phone_number,
        )

        if not user:

            return error_response(
                message="Unable to process request.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        validate_password(
            new_password,
            user=user,
        )

        user.set_password(new_password)

        user.save(
            update_fields=["password"],
        )

        cache.delete(
            f"pwd_reset_verified:{phone_number}"
        )

        return success_response(
            message="Password reset successfully.",
        )

    except ValueError as exc:

        return error_response(
            message=str(exc),
        )


# =========================================================
# NEWSLETTER
# =========================================================
@api_view(["POST"])
@permission_classes([AllowAny])
def subscribe_newsletter(
    request: Request,
) -> Response:
    """
    Subscribe newsletter.
    """

    serializer = NewsletterSubscribeSerializer(
        data=request.data,
    )

    if not serializer.is_valid():

        return error_response(
            message="Newsletter validation failed.",
            errors=serializer.errors,
        )

    email = serializer.validated_data["email"]

    subscriber, created = (
        NewsletterSubscriber.objects.get_or_create(
            email=email,
            defaults={
                "is_active": True,
            },
        )
    )

    if created:

        return success_response(
            message="Newsletter subscribed successfully.",
            data={
                "email": subscriber.email,
            },
            status_code=status.HTTP_201_CREATED,
        )

    if not subscriber.is_active:

        subscriber.is_active = True

        subscriber.save(
            update_fields=["is_active"],
        )

        return success_response(
            message="Newsletter subscription reactivated.",
        )

    return error_response(
        message="Email already subscribed.",
        status_code=status.HTTP_409_CONFLICT,
    )


# =========================================================
# ADMIN PASSWORD CHANGE
# =========================================================
class AdminPasswordChangeView(
    PasswordChangeView,
):
    template_name = (
        "registration/password_change_form.html"
    )

    def form_valid(
        self,
        form,
    ):

        response = super().form_valid(form)

        messages.success(
            self.request,
            (
                "Password changed successfully. "
                "Please login again."
            ),
        )

        logout(self.request)

        return response

    def get_success_url(self):

        return reverse_lazy("admin:login")