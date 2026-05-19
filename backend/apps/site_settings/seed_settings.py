from __future__ import annotations

import logging

from django.db import (
    transaction,
)

from .constants import (
    GENERAL_SETTINGS_FIELDS,
)
from .models import (
    SettingField,
    SettingGroup,
    SettingLevel,
)


logger = logging.getLogger(
    __name__
)


# =========================================================
# CREATE DEFAULT SETTINGS
# =========================================================
@transaction.atomic
def create_default_settings() -> None:
    """
    Seed default dynamic site settings.

    Safe to run multiple times.
    """

    logger.info(
        (
            "Starting default "
            "site settings seeding."
        )
    )

    # =====================================================
    # CREATE CORE LEVEL
    # =====================================================
    core_level, created = (
        SettingLevel.objects.update_or_create(
            key="core",
            defaults={
                "name": "Core",
                "order": 1,
                "is_active": True,
            },
        )
    )

    logger.info(
        (
            "SettingLevel processed | "
            "Key=%s | Created=%s"
        ),
        core_level.key,
        created,
    )

    # =====================================================
    # CREATE GENERAL SETTINGS GROUP
    # =====================================================
    general_group, created = (
        SettingGroup.objects.update_or_create(
            key="general-settings",
            defaults={
                "level": core_level,
                "name": (
                    "General Settings"
                ),
                "icon": (
                    "fa-solid fa-gear"
                ),
                "description": (
                    "Basic store "
                    "configuration and "
                    "website settings."
                ),
                "order": 1,
                "is_active": True,
            },
        )
    )

    logger.info(
        (
            "SettingGroup processed | "
            "Key=%s | Created=%s"
        ),
        general_group.key,
        created,
    )

    # =====================================================
    # CREATE DEFAULT FIELDS
    # =====================================================
    for index, field in enumerate(
        GENERAL_SETTINGS_FIELDS,
        start=1,
    ):

        field_key = field.get(
            "key"
        )

        if not field_key:

            logger.warning(
                (
                    "Skipped setting field "
                    "without key."
                )
            )

            continue

        field_type = field.get(
            "field_type"
        )

        # SUPPORT TextChoices / RAW STRING
        if hasattr(
            field_type,
            "value",
        ):
            field_type = (
                field_type.value
            )

        default_value = field.get(
            "default_value"
        )

        if default_value is None:
            default_value = ""

        setting_field, created = (
            SettingField.objects.update_or_create(
                group=general_group,
                key=field_key,
                defaults={

                    # BASIC
                    "label": field.get(
                        "label",
                        field_key,
                    ),

                    "field_type": (
                        field_type
                    ),

                    # CONTENT
                    "placeholder": (
                        field.get(
                            "placeholder",
                            "",
                        )
                    ),

                    "help_text": (
                        field.get(
                            "help_text",
                            "",
                        )
                    ),

                    # VALUES
                    "default_value": (
                        default_value
                    ),

                    "options": (
                        field.get(
                            "options"
                        )
                    ),

                    # FLAGS
                    "is_required": (
                        field.get(
                            "is_required",
                            False,
                        )
                    ),

                    "is_active": (
                        field.get(
                            "is_active",
                            True,
                        )
                    ),

                    # ORDERING
                    "order": field.get(
                        "order",
                        index,
                    ),
                },
            )
        )

        logger.info(
            (
                "SettingField processed | "
                "Key=%s | Created=%s"
            ),
            setting_field.key,
            created,
        )

    logger.info(
        (
            "Default site settings "
            "seeding completed "
            "successfully."
        )
    )