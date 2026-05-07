import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)

class AdminNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")

        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return
        
        if getattr(self.user, "role", None) not in ["admin", "manager"]:
            await self.close(code=4003)
            return
        
        self.group_name = f"admin_notifications_user_{self.user.id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        await self.accept()
        logger.info(
            "Admin notification WebSocket connected for user_id=%s",
            self.user.id,
        )

    async def disconnect(self, close_code):
        group_name = getattr(self, "group_name", None)

        if group_name:
            await self.channel_layer.group_discard(
                group_name,
                self.channel_name,
            )

        logger.info(
            "Admin notification WebSocket disconnected for user_id=%s code=%s",
            getattr(getattr(self, "user", None), "id", None),
            close_code,
        )

    async def send_notification(self, event):
        data = event.get("data")
        
        if not data:
            logger.warning("Empty notification event received")
            return
        
        await self.send(
            text_data=json.dumps(data)
        )