from __future__ import annotations

import json
import logging
from datetime import (
    date,
    datetime,
)
from decimal import Decimal
from uuid import UUID

from django.contrib.contenttypes.models import (
    ContentType,
)
from django.db import transaction
from django.db.models import (
    Model,
)
from django.db.models.signals import (
    post_delete,
    post_save,
    pre_save,
)

from apps.core.audit_middleware import (
    get_current_user,
)
from apps.core.models import AuditLog


logger = logging.getLogger(__name__)


# =========================================================
# AUDIT REGISTRY
# =========================================================
AUDITED_MODELS: set[type[Model]] = set()

IGNORE_FIELDS = frozenset(
    {
        "created_at",
        "updated_at",
    }
)

MAX_VALUE_LENGTH = 500


# =========================================================
# MODEL REGISTRATION
# =========================================================
def register_audit_model(
    model: type[Model],
) -> None:
    if model in AUDITED_MODELS:
        logger.debug(
            (
                "Audit model already "
                "registered: %s"
            ),
            model.__name__,
        )

        return

    AUDITED_MODELS.add(model)

    logger.info(
        (
            "Registered audit "
            "model: %s.%s"
        ),
        model._meta.app_label,
        model.__name__,
    )

    pre_save.connect(
        store_old_values,
        sender=model,
        weak=False,
        dispatch_uid=(
            f"audit_pre_save_"
            f"{model._meta.label_lower}"
        ),
    )

    post_save.connect(
        create_audit_log,
        sender=model,
        weak=False,
        dispatch_uid=(
            f"audit_post_save_"
            f"{model._meta.label_lower}"
        ),
    )

    post_delete.connect(
        create_delete_audit_log,
        sender=model,
        weak=False,
        dispatch_uid=(
            f"audit_post_delete_"
            f"{model._meta.label_lower}"
        ),
    )


# SERIALIZATION
def serialize_value(
    value,
) -> str | None:
    if value is None:
        return None

    if isinstance(
        value,
        (
            str,
            int,
            float,
            bool,
        ),
    ):
        return str(value)

    if isinstance(
        value,
        (
            datetime,
            date,
        ),
    ):
        return value.isoformat()

    if isinstance(
        value,
        Decimal,
    ):
        return str(value)

    if isinstance(
        value,
        UUID,
    ):
        return str(value)

    try:
        return json.dumps(
            value,
            default=str,
        )[:MAX_VALUE_LENGTH]

    except Exception:
        return str(value)[
            :MAX_VALUE_LENGTH
        ]


# PRE SAVE
def store_old_values(
    sender,
    instance: Model,
    **kwargs,
) -> None:
    if sender not in AUDITED_MODELS:

        return

    if not instance.pk:
        return

    if (
        sender._meta.abstract
        or sender._meta.proxy
    ):
        return

    try:
        old_instance = (
            sender.objects.get(
                pk=instance.pk,
            )
        )

    except sender.DoesNotExist:
        return

    changes: dict = {}

    for field in sender._meta.fields:

        field_name = field.name

        if (
            field_name
            in IGNORE_FIELDS
        ):
            continue

        old_value = getattr(
            old_instance,
            field_name,
            None,
        )

        new_value = getattr(
            instance,
            field_name,
            None,
        )

        if old_value == new_value:
            continue

        changes[field_name] = {
            "old": serialize_value(
                old_value,
            ),
            "new": serialize_value(
                new_value,
            ),
        }

    instance._audit_changes = (
        changes
    )


# POST SAVE
def create_audit_log(
    sender,
    instance: Model,
    created: bool,
    **kwargs,
) -> None:
    if sender not in AUDITED_MODELS:

        return

    if (
        sender._meta.abstract
        or sender._meta.proxy
    ):

        return

    action = (
        AuditLog.Action.CREATED
        if created
        else AuditLog.Action.UPDATED
    )

    changes = (
        {}
        if created
        else getattr(
            instance,
            "_audit_changes",
            {},
        )
    )

    if (
        not created
        and not changes
    ):
        return

    model_name = (
        sender._meta.label
    )

    actor = get_current_user()

    def save_audit_log():

        try:

            AuditLog.objects.create(
                actor=actor,
                action=action,
                content_type=(
                    ContentType.objects.get_for_model(
                        sender,
                    )
                ),
                object_id=instance.pk,
                object_repr=(
                    f"{model_name} - "
                    f"{str(instance)}"
                )[:255],
                changes=changes,
            )

        except Exception as exc:

            logger.exception(
                (
                    "Failed to create "
                    "audit log: %s"
                ),
                exc,
            )

    transaction.on_commit(
        save_audit_log,
    )


# POST DELETE
def create_delete_audit_log(
    sender,
    instance: Model,
    **kwargs,
) -> None:
    if sender not in AUDITED_MODELS:

        return

    if (
        sender._meta.abstract
        or sender._meta.proxy
    ):

        return

    actor = get_current_user()

    model_name = (
        sender._meta.label
    )

    def save_audit_log():

        try:
            AuditLog.objects.create(
                actor=actor,
                action=(
                    AuditLog.Action.DELETED
                ),
                content_type=(
                    ContentType.objects.get_for_model(
                        sender,
                    )
                ),
                object_id=instance.pk,
                object_repr=(
                    f"{model_name} - "
                    f"{str(instance)}"
                )[:255],
                changes={},
            )

        except Exception as exc:
            logger.exception(
                (
                    "Failed to create "
                    "delete audit log: %s"
                ),
                exc,
            )

    transaction.on_commit(
        save_audit_log,
    )