import logging

from typing import Optional, Tuple, Any

from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.backends import ModelBackend
from django.http import HttpRequest
from django.utils import timezone

from rest_framework_simplejwt.authentication import (
    JWTAuthentication,
)
from rest_framework_simplejwt.exceptions import (
    InvalidToken,
    TokenError,
)

from rest_framework_simplejwt.tokens import Token

User = get_user_model()

logger = logging.getLogger(__name__)

INVALID_JWT_LOG_CACHE_KEY: str = (
    "auth:invalid_jwt_log_throttle"
)

JWT_LOG_THROTTLE_TIMEOUT: int = 60


# --------------- EMAIL LOGIN BACKEND --------------- #
class EmailBackend(ModelBackend):
    """
    Authenticate users using email and password.
    """

    def authenticate(
        self,
        request: Optional[HttpRequest],
        username: Optional[str] = None,
        password: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[AbstractBaseUser]:
        email = (
            kwargs.get("email")
            or username
            or ""
        ).strip().lower()

        if not email or not password:
            return None
        
        try:
            user = User.objects.only(
                "id",
                "email",
                "password",
                "is_active",
            ).get(email__iexact=email)

        except User.DoesNotExist:
            return None
        
        if (
            user.check_password(password)
            and self.user_can_authenticate(user)
        ):
            return user
        
        return None
    
# --------------- COOKIE JWT AUTH --------------- #    
class CookieJWTAuthentication(JWTAuthentication):
    """
    Authenticate JWT tokens from secure HTTP-only cookies.
    """

    def authenticate(
        self,
        request: HttpRequest,
    ) -> Optional[Tuple[AbstractBaseUser, Token]]:
        
        # JWT token stored in secure HTTP-only cookie.
        raw_token = request.COOKIES.get(
            settings.SIMPLE_JWT.get(
                "AUTH_COOKIE",
                "access_token",
            )
        )

        if raw_token is None:
            return None
        
        try:
            validated_token = (
                self.get_validated_token(raw_token)
            )
            user = self.get_user(validated_token)
            return (
                user,
                validated_token,
            )
        
        except (InvalidToken, TokenError):

            last_log_time = cache.get(
                INVALID_JWT_LOG_CACHE_KEY,
                0,
            )

            current_time = (
                timezone.now().timestamp()
            )

            if (
                current_time - last_log_time
                > JWT_LOG_THROTTLE_TIMEOUT
            ):

                logger.warning(
                    "Invalid JWT token received.",
                    extra={
                        "path": request.path,
                        "method": request.method,
                    }
                )

                cache.set(
                    INVALID_JWT_LOG_CACHE_KEY,
                    current_time,
                    timeout=JWT_LOG_THROTTLE_TIMEOUT,
                )

            return None