from __future__ import annotations

import logging
from functools import partial

from django.core.exceptions import (
    ValidationError,
)
from django.db import (
    transaction,
)

from apps.accounts.models import (
    User,
)

from apps.products.notifications.models import (
    AdminNotification,
)

from apps.products.notifications.utils import (
    broadcast_admin_notification,
)


logger = logging.getLogger(
    __name__
)


# =========================================================
# CREATE ADMIN NOTIFICATION
# =========================================================
@transaction.atomic
def create_admin_notification(
    *,
    title: str,
    message: str,
    notification_type: str = (
        AdminNotification.Type.SYSTEM
    ),
    url: str | None = None,
    user: User | None = None,
) -> AdminNotification:
    
    # VALIDATE NOTIFICATION TYPE
    if (
        notification_type
        not in AdminNotification.Type.values
    ):
        raise ValidationError(
            (
                "Invalid notification "
                f"type: {notification_type}"
            )
        )

    # CREATE NOTIFICATION
    notification = (
        AdminNotification.objects.create(
            title=title,
            message=message,
            notification_type=(
                notification_type
            ),
            url=url,
            created_for=user,
        )
    )

    logger.info(
        (
            "Admin notification created "
            "successfully: id=%s type=%s"
        ),
        notification.id,
        notification.notification_type,
    )

    # REALTIME BROADCAST
    def send_notification(
        notification_instance: (
            AdminNotification
        ),
    ) -> None:
        try:
            broadcast_admin_notification(
                notification_instance,
            )

            logger.info(
                (
                    "Admin notification "
                    "broadcast successfully: "
                    "id=%s"
                ),
                notification_instance.id,
            )

        except Exception:
            logger.exception(
                (
                    "Failed to broadcast "
                    "admin notification: "
                    "id=%s"
                ),
                notification_instance.id,
            )

    transaction.on_commit(
        partial(
            send_notification,
            notification,
        )
    )

    return notification