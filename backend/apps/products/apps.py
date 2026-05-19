from __future__ import annotations

import logging

from django.apps import (
    AppConfig,
)


logger = logging.getLogger(
    __name__
)


# =========================================================
# PRODUCTS APP CONFIG
# =========================================================
class ProductsConfig(
    AppConfig,
):
    default_auto_field = (
        "django.db.models.BigAutoField"
    )

    name = "apps.products"

    verbose_name = (
        "Products"
    )

    _is_initialized = False

    # DJANGO READY HOOK
    def ready(
        self,
    ) -> None:

        # PREVENT DUPLICATE INITIALIZATION
        if self.__class__._is_initialized:

            logger.debug(
                (
                    "ProductsConfig already "
                    "initialized. "
                    "Skipping duplicate setup."
                )
            )

            return

        logger.info(
            (
                "Initializing Products "
                "application."
            )
        )

        try:

            # REGISTER SIGNALS
            from apps.products import (
                signals,
            )

            self.__class__._is_initialized = (
                True
            )

            logger.info(
                (
                    "Products application "
                    "initialized successfully."
                )
            )

        except Exception as exc:
            logger.exception(
                (
                    "Failed to initialize "
                    "Products application: %s"
                ),
                exc,
            )

            raise