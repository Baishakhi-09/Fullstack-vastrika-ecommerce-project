from __future__ import annotations

import logging

from django.db import transaction
from django.db.models.signals import (
    post_save,
    pre_save,
)
from django.dispatch import receiver

from apps.orders.models import (
    Order,
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
# ORDER STATUS NOTIFICATION MESSAGES
# =========================================================
ORDER_STATUS_MESSAGES = {
    Order.Status.PAID: (
        "Payment received"
    ),
    Order.Status.PACKED: (
        "Order packed"
    ),
    Order.Status.SHIPPED: (
        "Order shipped"
    ),
    Order.Status.OUT_FOR_DELIVERY: (
        "Order is out for delivery"
    ),
    Order.Status.DELIVERED: (
        "Order delivered"
    ),
    Order.Status.CANCELLED: (
        "Order cancelled"
    ),
    Order.Status.RETURN_REQUESTED: (
        "Return requested"
    ),
    Order.Status.RETURN_APPROVED: (
        "Return approved"
    ),
    Order.Status.RETURN_PICKED: (
        "Return picked"
    ),
    Order.Status.RETURNED: (
        "Order returned"
    ),
    Order.Status.REFUNDED: (
        "Refund completed"
    ),
}


# =========================================================
# STORE PREVIOUS ORDER STATUS
# =========================================================
@receiver(
    pre_save,
    sender=Order,
)
def store_old_order_status(
    sender,
    instance: Order,
    **kwargs,
) -> None:
    """
    Store previous order status
    before update.
    """

    if not instance.pk:

        instance._old_status = (
            None
        )

        return

    previous_status = (
        Order.objects.filter(
            pk=instance.pk,
        )
        .values_list(
            "status",
            flat=True,
        )
        .first()
    )

    instance._old_status = (
        previous_status
    )


# =========================================================
# CREATE ORDER NOTIFICATIONS
# =========================================================
@receiver(
    post_save,
    sender=Order,
)
def create_order_notification(
    sender,
    instance: Order,
    created: bool,
    **kwargs,
) -> None:
    """
    Create admin notifications
    for important order events.
    """

    try:
        notification_data = None

        # ORDER CREATED
        if created:
            notification_data = {
                "title": (
                    "New Order Placed"
                ),
                "message": (
                    f"New order "
                    f"#{instance.order_number} "
                    f"has been placed."
                ),
            }

        # ORDER STATUS UPDATED
        else:

            old_status = getattr(
                instance,
                "_old_status",
                None,
            )

            # SKIP DUPLICATE STATUS EVENTS
            if (
                old_status
                == instance.status
            ):
                return

            status_message = (
                ORDER_STATUS_MESSAGES.get(
                    instance.status,
                )
            )

            if not status_message:
                return

            notification_data = {
                "title": (
                    status_message
                ),
                "message": (
                    f"Order "
                    f"#{instance.order_number}: "
                    f"{status_message}."
                ),
            }

        # NO NOTIFICATION REQUIRED
        if not notification_data:
            return

        # CREATE NOTIFICATION
        # AFTER TRANSACTION COMMIT
        def send_notification() -> None:

            try:

                notification = (
                    AdminNotification.objects.create(
                        title=notification_data[
                            "title"
                        ],
                        message=notification_data[
                            "message"
                        ],
                        notification_type=(
                            AdminNotification.Type.ORDER
                        ),
                        url=(
                            "/admin/orders/order/"
                            f"{instance.id}/change/"
                        ),
                    )
                )

                broadcast_admin_notification(
                    notification,
                )

                logger.info(
                    (
                        "Order notification "
                        "created successfully "
                        "for order #%s."
                    ),
                    instance.order_number,
                )

            except Exception:
                logger.exception(
                    (
                        "Failed to create "
                        "order notification "
                        "for order #%s."
                    ),
                    instance.order_number,
                )

        transaction.on_commit(
            send_notification,
        )

    except Exception:
        logger.exception(
            (
                "Unexpected failure while "
                "processing order signals "
                "for order #%s."
            ),
            instance.order_number,
        )