import logging

from http.cookies import SimpleCookie
from urllib.parse import parse_qs
from typing import Optional

from channels.db import (
    database_sync_to_async,
)

from django.contrib.auth.models import (
    AnonymousUser,
)

from rest_framework_simplejwt.authentication import (
    JWTAuthentication,
)

from rest_framework_simplejwt.exceptions import (
    InvalidToken,
    TokenError,
    AuthenticationFailed,
)


logger = logging.getLogger(__name__)


# =========================================================
# CONSTANTS
# =========================================================

ACCESS_TOKEN_COOKIE_NAME = (
    "access_token"
)


# =========================================================
# TOKEN HELPERS
# =========================================================

def extract_token_from_cookies(
    scope: dict,
) -> Optional[str]:
    """
    Extract JWT token from cookies.
    """

    headers = dict(
        scope.get("headers", [])
    )

    raw_cookie = headers.get(
        b"cookie",
        b"",
    ).decode()

    if not raw_cookie:
        return None

    cookie = SimpleCookie()

    try:
        cookie.load(raw_cookie)

    except Exception:

        logger.warning(
            "Invalid websocket "
            "cookie header."
        )

        return None

    access_cookie = cookie.get(
        ACCESS_TOKEN_COOKIE_NAME
    )

    if not access_cookie:
        return None

    return access_cookie.value


def extract_token_from_query(
    scope: dict,
) -> Optional[str]:
    """
    Extract JWT token from
    websocket query params.
    """

    query_string = (
        scope.get(
            "query_string",
            b"",
        ).decode()
    )

    query_params = parse_qs(
        query_string
    )

    return query_params.get(
        "token",
        [None],
    )[0]


def extract_token_from_scope(
    scope: dict,
) -> Optional[str]:
    """
    Extract JWT token from scope.
    """

    token = (
        extract_token_from_cookies(
            scope,
        )
    )

    if token:
        return token

    return extract_token_from_query(
        scope,
    )


# =========================================================
# JWT USER RESOLUTION
# =========================================================

@database_sync_to_async
def get_user_from_token(
    token: str,
):
    """
    Resolve authenticated user
    from JWT token.
    """

    try:

        jwt_auth = JWTAuthentication()

        validated_token = (
            jwt_auth.get_validated_token(
                token,
            )
        )

        return jwt_auth.get_user(
            validated_token,
        )

    except (
        InvalidToken,
        TokenError,
        AuthenticationFailed,
    ):

        logger.warning(
            "Invalid websocket JWT token."
        )

        return AnonymousUser()

    except Exception:

        logger.exception(
            "Unexpected websocket "
            "authentication error."
        )

        return AnonymousUser()


# =========================================================
# JWT AUTH MIDDLEWARE
# =========================================================

class JWTAuthMiddleware:
    """
    JWT websocket authentication
    middleware.
    """

    def __init__(
        self,
        app,
    ):
        self.app = app

    async def __call__(
        self,
        scope,
        receive,
        send,
    ):

        if (
            scope.get("type")
            != "websocket"
        ):
            return await self.app(
                scope,
                receive,
                send,
            )

        token = (
            extract_token_from_scope(
                scope,
            )
        )

        if token:

            scope["user"] = (
                await get_user_from_token(
                    token,
                )
            )

        else:
            scope["user"] = (
                AnonymousUser()
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
    app,
):
    """
    JWT websocket middleware stack.
    """

    return JWTAuthMiddleware(
        app,
    )