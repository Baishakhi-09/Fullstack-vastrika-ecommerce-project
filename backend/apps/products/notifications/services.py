from django.db import transaction
from django.core.exceptions import ValidationError

from .models import AdminNotification
from .utils import broadcast_admin_notification

@transaction.atomic
def create_admin_notification(
    *,
    title: str,
    message: str,
    notification_type: str = AdminNotification.Type.SYSTEM.value,
    url: str | None = None,
    user=None,
):
    # Validate notification type
    if notification_type not in AdminNotification.Type.values:
        raise ValidationError("Invalid notification type")
    
    notification = AdminNotification.objects.create(
        title=title,
        message=message,
        notification_type=notification_type,
        url=url,
        created_for=user,
    )

    # Send real-time notification
    transaction.on_commit(
        lambda n=notification: broadcast_admin_notification(n)
    )

    return notification