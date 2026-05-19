from __future__ import annotations

import logging

from django.apps import (
    AppConfig,
)


logger = logging.getLogger(
    __name__
)


# =========================================================
# ORDERS APP CONFIG
# =========================================================
class OrdersConfig(
    AppConfig,
):
    default_auto_field = (
        "django.db.models.BigAutoField"
    )

    name = "apps.orders"

    verbose_name = (
        "Orders"
    )

    _is_initialized = False

    # DJANGO READY HOOK
    def ready(
        self,
    ) -> None:
        if self.__class__._is_initialized:

            logger.debug(
                (
                    "OrdersConfig already "
                    "initialized. "
                    "Skipping duplicate setup."
                )
            )

            return

        logger.info(
            (
                "Initializing Orders "
                "application."
            )
        )

        try:

            # REGISTER SIGNALS
            from apps.orders import (
                signals,
            )

            self.__class__._is_initialized = (
                True
            )

            logger.info(
                (
                    "Orders application "
                    "initialized successfully."
                )
            )

        except Exception as exc:
            logger.exception(
                (
                    "Failed to initialize "
                    "Orders application: %s"
                ),
                exc,
            )

            raise