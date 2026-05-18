from __future__ import annotations

import logging
from http.cookies import SimpleCookie
from typing import Any
from urllib.parse import parse_qs

from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async

from django.contrib.auth.models import (
    AnonymousUser,
)

from rest_framework_simplejwt.authentication import (
    JWTAuthentication,
)
from rest_framework_simplejwt.exceptions import (
    InvalidToken,
    TokenError,
)

logger = logging.getLogger(__name__)


# =========================================================
# CONSTANTS
# =========================================================
ACCESS_TOKEN_COOKIE = "access_token"

QUERY_TOKEN_PARAM = "token"

ENABLE_QUERY_TOKEN_FALLBACK = True


# =========================================================
# TOKEN HELPERS
# =========================================================
@database_sync_to_async
def get_user_from_token(
    token: str | None,
) -> Any:
    """
    Validate JWT token and return authenticated user.

    Args:
        token (str | None):
            Raw JWT token.

    Returns:
        Authenticated user instance
        or AnonymousUser.
    """

    if not token:

        logger.debug(
            "WebSocket auth skipped: Missing token."
        )

        return AnonymousUser()

    try:

        jwt_auth = JWTAuthentication()

        validated_token = (
            jwt_auth.get_validated_token(
                token,
            )
        )

        user = jwt_auth.get_user(
            validated_token,
        )

        logger.info(
            (
                "WebSocket JWT authentication "
                "successful for user '%s'."
            ),
            getattr(
                user,
                "username",
                "unknown",
            ),
        )

        return user

    except (
        InvalidToken,
        TokenError,
    ) as exc:

        logger.warning(
            (
                "Invalid WebSocket JWT token: %s"
            ),
            exc,
        )

        return AnonymousUser()

    except Exception as exc:

        logger.exception(
            (
                "Unexpected WebSocket "
                "authentication error: %s"
            ),
            exc,
        )

        return AnonymousUser()


# =========================================================
# COOKIE TOKEN EXTRACTION
# =========================================================
def extract_token_from_cookies(
    headers: dict[bytes, bytes],
) -> str | None:
    """
    Extract JWT token from cookies.

    Args:
        headers:
            ASGI request headers.

    Returns:
        JWT token or None.
    """

    raw_cookie = headers.get(
        b"cookie",
        b"",
    ).decode()

    if not raw_cookie:

        return None

    try:

        cookie = SimpleCookie()

        cookie.load(raw_cookie)

        token = cookie.get(
            ACCESS_TOKEN_COOKIE,
        )

        if not token:

            return None

        return token.value

    except Exception as exc:

        logger.warning(
            (
                "Failed to parse WebSocket "
                "cookies: %s"
            ),
            exc,
        )

        return None


# =========================================================
# QUERY TOKEN EXTRACTION
# =========================================================
def extract_token_from_query(
    scope: dict[str, Any],
) -> str | None:
    if not ENABLE_QUERY_TOKEN_FALLBACK:

        return None

    query_string = scope.get(
        "query_string",
        b"",
    ).decode()

    if not query_string:

        return None

    query_params = parse_qs(
        query_string,
    )

    token = query_params.get(
        QUERY_TOKEN_PARAM,
        [None],
    )[0]

    return token


# =========================================================
# JWT AUTH MIDDLEWARE
# =========================================================
class JWTAuthMiddleware:
    def __init__(
        self,
        app,
    ) -> None:

        self.app = app

    async def __call__(
        self,
        scope: dict[str, Any],
        receive,
        send,
    ) -> Any:
        """
        Authenticate WebSocket connection.
        """

        headers = dict(
            scope.get(
                "headers",
                [],
            )
        )

        token = extract_token_from_cookies(
            headers,
        )

        if not token:

            token = extract_token_from_query(
                scope,
            )

        scope["user"] = (
            await get_user_from_token(
                token,
            )
        )

        return await self.app(
            scope,
            receive,
            send,
        )


# =========================================================
# MIDDLEWARE STACK
# =========================================================
def JWTAuthMiddlewareStack(
    inner,
):
    return JWTAuthMiddleware(
        AuthMiddlewareStack(
            inner,
        ),
    )