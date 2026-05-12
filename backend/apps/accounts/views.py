# backend/apps/accounts/views/auth.py

import logging

from django.conf import settings
from django.contrib.auth import authenticate, logout
from django.core.cache import cache

from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import (
    RefreshToken,
    TokenError,
)

from .authentication import (
    CookieJWTAuthentication,
)

from .serializers import (
    SignupSerializer,
    ProfileSerializer,
)

from .utils import (
    normalize_phone,
    mask_phone,
)

from twilio import (
    send_verification_code,
    check_verification_code,
)

from .models import User


logger = logging.getLogger(__name__)


# =========================================================
# HELPERS
# =========================================================

ACCESS_COOKIE_NAME = "access_token"
REFRESH_COOKIE_NAME = "refresh_token"

ACCESS_TOKEN_MAX_AGE = 60 * 60
REFRESH_TOKEN_MAX_AGE = 60 * 60 * 24 * 7


def set_auth_cookies(
    response: Response,
    refresh: RefreshToken,
) -> None:
    """
    Set JWT auth cookies.
    """

    response.set_cookie(
        key=ACCESS_COOKIE_NAME,
        value=str(refresh.access_token),
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
        max_age=ACCESS_TOKEN_MAX_AGE,
        path="/",
    )

    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=str(refresh),
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
    Remove auth cookies.
    """

    response.delete_cookie(
        ACCESS_COOKIE_NAME,
        path="/",
    )

    response.delete_cookie(
        REFRESH_COOKIE_NAME,
        path="/",
    )


def get_user_payload(
    user: User,
) -> dict:
    """
    Serialize authenticated user payload.
    """

    return {
        "id": user.id,
        "first_name": user.first_name,
        "email": user.email,
        "phone": user.phone,
        "alternate_phone": (
            user.alternate_phone
        ),
        "gender": user.gender,
        "address_line_1": (
            user.address_line_1
        ),
        "address_line_2": (
            user.address_line_2
        ),
        "city": user.city,
        "state": user.state,
        "pincode": user.pincode,
        "country": user.country,
        "role": user.role,
        "role_display": (
            user.get_role_display()
        ),
    }


def get_password_reset_cache_key(
    phone_number: str,
) -> str:
    """
    Generate password reset cache key.
    """

    return (
        f"pwd_reset_verified:"
        f"{phone_number}"
    )


# =========================================================
# LOGIN
# =========================================================

@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):

    username = (
        request.data.get(
            "username",
            "",
        ).strip()
    )

    password = request.data.get(
        "password",
        "",
    )

    if not username or not password:
        return Response(
            {
                "success": False,
                "error": (
                    "Username and password "
                    "are required."
                ),
            },
            status=(
                status.HTTP_400_BAD_REQUEST
            ),
        )

    user = authenticate(
        request=request,
        username=username,
        password=password,
    )

    if user is None:

        logger.warning(
            "Failed login attempt "
            "for username=%s",
            username,
        )

        return Response(
            {
                "success": False,
                "error": (
                    "Invalid username "
                    "or password."
                ),
            },
            status=(
                status.HTTP_401_UNAUTHORIZED
            ),
        )

    refresh = RefreshToken.for_user(
        user,
    )

    response = Response(
        {
            "success": True,
            "message": (
                "Login successful."
            ),
            "user": (
                get_user_payload(user)
            ),
        },
        status=status.HTTP_200_OK,
    )

    set_auth_cookies(
        response,
        refresh,
    )

    return response


# =========================================================
# SIGNUP
# =========================================================

@api_view(["POST"])
@permission_classes([AllowAny])
def signup(request):

    serializer = SignupSerializer(
        data=request.data,
    )

    if not serializer.is_valid():

        return Response(
            {
                "success": False,
                "errors": (
                    serializer.errors
                ),
            },
            status=(
                status.HTTP_400_BAD_REQUEST
            ),
        )

    try:

        user = serializer.save()

        refresh = (
            RefreshToken.for_user(user)
        )

        response = Response(
            {
                "success": True,
                "message": (
                    "Account created "
                    "successfully."
                ),
                "user": (
                    get_user_payload(user)
                ),
            },
            status=(
                status.HTTP_201_CREATED
            ),
        )

        set_auth_cookies(
            response,
            refresh,
        )

        return response

    except Exception:

        logger.exception(
            "Signup failed."
        )

        return Response(
            {
                "success": False,
                "error": (
                    "Something went wrong. "
                    "Please try again."
                ),
            },
            status=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
        )


# =========================================================
# LOGOUT
# =========================================================

@api_view(["POST"])
@permission_classes([AllowAny])
def logout_view(request):

    refresh_token = request.COOKIES.get(
        REFRESH_COOKIE_NAME,
    )

    if refresh_token:

        try:
            token = RefreshToken(
                refresh_token,
            )

            token.blacklist()

        except TokenError:
            pass

        except Exception:

            logger.exception(
                "JWT blacklist failed."
            )

    logout(request)

    response = Response(
        {
            "success": True,
            "message": (
                "Logout successful."
            ),
        },
        status=status.HTTP_200_OK,
    )

    clear_auth_cookies(
        response,
    )

    return response


# =========================================================
# SESSION STATUS
# =========================================================

@api_view(["GET"])
@authentication_classes([
    CookieJWTAuthentication,
])
@permission_classes([AllowAny])
def session_status(request):

    if (
        request.user
        and request.user.is_authenticated
    ):

        return Response(
            {
                "authenticated": True,
                "user": (
                    get_user_payload(
                        request.user
                    )
                ),
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


# =========================================================
# USER PROFILE
# =========================================================

@api_view(["GET"])
@authentication_classes([
    CookieJWTAuthentication,
])
@permission_classes([
    IsAuthenticated,
])
def profile(request):

    serializer = ProfileSerializer(
        request.user,
    )

    return Response(
        serializer.data,
        status=status.HTTP_200_OK,
    )


@api_view(["PATCH"])
@authentication_classes([
    CookieJWTAuthentication,
])
@permission_classes([
    IsAuthenticated,
])
def update_profile(request):

    serializer = ProfileSerializer(
        request.user,
        data=request.data,
        partial=True,
    )

    if not serializer.is_valid():

        return Response(
            {
                "success": False,
                "errors": (
                    serializer.errors
                ),
            },
            status=(
                status.HTTP_400_BAD_REQUEST
            ),
        )

    serializer.save()

    return Response(
        {
            "success": True,
            "message": (
                "Profile updated "
                "successfully."
            ),
            "user": serializer.data,
        },
        status=status.HTTP_200_OK,
    )