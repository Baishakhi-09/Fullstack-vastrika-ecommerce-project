from __future__ import annotations

import logging
from contextvars import (
    ContextVar,
    Token,
)
from typing import Callable

from django.contrib.auth.models import (
    AnonymousUser,
)
from django.http import (
    HttpRequest,
    HttpResponse,
)

from apps.accounts.models import User


logger = logging.getLogger(__name__)


# AUDIT USER CONTEXT
_current_user: ContextVar[
    User | None
] = ContextVar(
    "current_audit_user",
    default=None,
)


# USER CONTEXT HELPERS
def set_current_user(
    user: User | None,
) -> Token:
    return _current_user.set(
        user,
    )


def get_current_user(
) -> User | None:
    return _current_user.get()


def reset_current_user(
    token: Token,
) -> None:
    _current_user.reset(
        token,
    )


# =========================================================
# AUDIT USER MIDDLEWARE
# =========================================================
class AuditUserMiddleware:

    def __init__(
        self,
        get_response: Callable,
    ) -> None:
        self.get_response = (
            get_response
        )

    def __call__(
        self,
        request: HttpRequest,
    ) -> HttpResponse:
        user = getattr(
            request,
            "user",
            None,
        )

        if isinstance(
            user,
            AnonymousUser,
        ):
            user = None

        token = set_current_user(
            user,
        )

        logger.debug(
            (
                "Audit user context "
                "initialized."
            )
        )

        try:
            response = self.get_response(
                request,
            )

            return response

        finally:
            reset_current_user(
                token,
            )

            logger.debug(
                (
                    "Audit user context "
                    "reset successfully."
                )
            )