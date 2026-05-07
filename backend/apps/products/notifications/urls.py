from django.urls import path
from . import views

urlpatterns = [
    path("", views.api_admin_notifications, name="list_notifications"),
    path("read-all/", views.api_mark_all_notifications_read, name="mark_all_notifications_read"),
    path("<int:notification_id>/mark-read/", views.api_mark_notification_read, name="mark_notification_read"),
]