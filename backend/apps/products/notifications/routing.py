from __future__ import annotations

from django.urls import (
    path,
)

from apps.products.notifications.consumers import (
    AdminNotificationConsumer,
)


# =========================================================
# WEBSOCKET ROUTES
# =========================================================
app_name = (
    "product_notifications"
)

websocket_urlpatterns = [
    path(
        "ws/admin/notifications/",
        AdminNotificationConsumer.as_asgi(),
        name="admin_notifications_ws",
    ),
]