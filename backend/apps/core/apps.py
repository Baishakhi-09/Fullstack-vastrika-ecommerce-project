from __future__ import annotations

import logging
from typing import Type

from django.apps import (
    AppConfig,
    apps,
)
from django.db.models import Model


logger = logging.getLogger(__name__)


# =========================================================
# CORE CONFIG
# =========================================================
class CoreConfig(AppConfig):
    default_auto_field = (
        "django.db.models.BigAutoField"
    )

    name = "apps.core"

    verbose_name = "Core"

    _is_initialized = False

    # DJANGO READY HOOK
    def ready(
        self,
    ) -> None:
        if self.__class__._is_initialized:
            logger.debug(
                (
                    "CoreConfig already initialized. "
                    "Skipping duplicate setup."
                )
            )

            return

        logger.info(
            (
                "Initializing core "
                "application configuration."
            )
        )

        try:
            self.register_audit_models()

            self.__class__._is_initialized = True

            logger.info(
                (
                    "Core application "
                    "initialized successfully."
                )
            )

        except Exception as exc:
            logger.exception(
                (
                    "Failed to initialize "
                    "CoreConfig: %s"
                ),
                exc,
            )

            raise

    # AUDIT REGISTRATION
    def register_audit_models(
        self,
    ) -> None:
        """
        Dynamically register all auditable models.
        """

        from apps.core.audit_signals import (
            register_audit_model,
        )

        registered_count = 0

        for model in apps.get_models():

            if not self.is_auditable_model(
                model,
            ):
                continue

            try:
                register_audit_model(
                    model,
                )

                registered_count += 1

                logger.info(
                    (
                        "Registered audit model: "
                        "%s.%s"
                    ),
                    model._meta.app_label,
                    model.__name__,
                )

            except Exception as exc:
                logger.exception(
                    (
                        "Failed to register "
                        "audit model %s: %s"
                    ),
                    model.__name__,
                    exc,
                )

        logger.info(
            (
                "Successfully registered "
                "%s audit models."
            ),
            registered_count,
        )

    # AUDITABLE MODEL DETECTION
    @staticmethod
    def is_auditable_model(
        model: Type[Model],
    ) -> bool:
        return bool(
            getattr(
                model,
                "audit_enabled",
                False,
            )
        )