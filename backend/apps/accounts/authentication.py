from __future__ import annotations

import logging
from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.http import HttpRequest
from django.contrib.auth.models import AbstractBaseUser

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import (
    InvalidToken,
    TokenError,
)

logger = logging.getLogger(__name__)

User = get_user_model()


# EMAIL AUTHENTICATION BACKEND
class EmailBackend(ModelBackend):
    def authenticate(
        self,
        request: HttpRequest | None,
        username: str | None = None,
        password: str | None = None,
        **kwargs: Any,
    ) -> AbstractBaseUser | None:
        """
        Authenticate user using email and password.
        """

        email = (
            kwargs.get("email")
            or username
            or ""
        ).strip().lower()

        if not email or not password:

            logger.debug(
                "Authentication failed: Missing email or password."
            )

            return None

        user = User.objects.filter(
            email__iexact=email,
        ).first()

        if not user:

            logger.warning(
                "Authentication failed: User not found.",
                email,
            )

            return None

        if not self.user_can_authenticate(user):

            logger.warning(
                "Authentication blocked: User inactive '%s'.",
                email,
            )

            return None

        if not user.check_password(password):

            logger.warning(
                "Authentication failed: Invalid password for '%s'.",
                email,
            )

            return None

        logger.info(
            "Authentication successful for '%s'.",
            email,
        )

        return user


# JWT COOKIE AUTHENTICATION
class CookieJWTAuthentication(JWTAuthentication):
    cookie_name = "access_token"

    def authenticate(
        self,
        request: HttpRequest,
    ) -> tuple[AbstractBaseUser, Any] | None:
        """
        Authenticate user from JWT access token cookie.
        """

        raw_token = request.COOKIES.get(
            self.cookie_name,
        )

        if not raw_token:

            logger.debug(
                "JWT authentication skipped: No access token cookie."
            )

            return None

        try:

            validated_token = self.get_validated_token(
                raw_token,
            )

            user = self.get_user(validated_token)

            logger.info(
                "JWT authentication successful for user '%s'.",
                user,
            )

            return (
                user,
                validated_token,
            )

        except (InvalidToken, TokenError) as exc:

            logger.warning(
                "JWT authentication failed: %s",
                exc,
            )

            return None