from __future__ import annotations

from django.urls import path

from . import views


app_name = "vastrika_product_notifications"


# API ROUTES
urlpatterns = [

    # LIST ADMIN NOTIFICATIONS
    path(
        "admin-notifications/",
        views.api_admin_notifications,
        name="admin_notification_list",
    ),

    # MARK ALL NOTIFICATIONS AS READ
    path(
        "admin-notifications/mark-all-read/",
        views.api_mark_all_notifications_read,
        name="admin_notification_mark_all_read",
    ),

    # MARK SINGLE NOTIFICATION AS READ
    path(
       "admin-notifications/<int:notification_id>/mark-read/",
        views.api_mark_notification_read,
        name="admin_notification_mark_read",
    ),
]