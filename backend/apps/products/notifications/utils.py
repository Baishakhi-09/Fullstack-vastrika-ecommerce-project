import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .serializers import AdminNotificationSerializer

logger = logging.getLogger(__name__)


def broadcast_admin_notification(notification):
    if not notification.created_for_id:
        logger.info("Skipped broadcast: notification has no created_for user")
        return
    
    channel_layer = get_channel_layer()
    if not channel_layer:
        logger.warning("Skipped broadcast: channel layer not configured")
        return

    data = AdminNotificationSerializer(notification).data
    group_name = f"admin_notifications_user_{notification.created_for_id}"

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "send_notification",
            "data": {
                "event": "new_notification",
                "notification": data,
            },
        },
    )

    logger.info(
        "Broadcasted notification to user_id=%s",
        notification.created_for_id,
    )