from django.db.models import Q, Exists, OuterRef
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.utils.timezone import localtime

from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)

from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework import status

from rest_framework.permissions import IsAdminUser

from .models import AdminNotification, AdminNotificationRead
from .serializers import AdminNotificationSerializer

# =====================================================
# API VIEWS - FOR FRONTEND / REACT ADMIN PANEL
# =====================================================

@api_view(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAdminUser])
def api_admin_notifications(request):
    read_subquery = AdminNotificationRead.objects.filter(
        user=request.user,
        notification=OuterRef("pk"),
    )

    queryset = AdminNotification.objects.filter(
        Q(created_for=request.user) | Q(created_for__isnull=True)
    ).annotate(
        is_read=Exists(read_subquery)
    )

    notifications = queryset.order_by("-created_at")[:20]

    unread_count = queryset.filter(
        is_read=False
    ).count()

    serializer = AdminNotificationSerializer(notifications, many=True)

    return Response(
        {
            "count": unread_count,
            "unread_count": unread_count,
            "notifications": serializer.data,
        },
        status=status.HTTP_200_OK,
    )

@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAdminUser])
def api_mark_notification_read(request, notification_id):
    notification = get_object_or_404(
        AdminNotification,
        Q(created_for=request.user) | Q(created_for__isnull=True),
        id=notification_id,
    )

    AdminNotificationRead.objects.get_or_create(
        user=request.user,
        notification=notification,
    )

    return Response(
        {"success": True},
        status=status.HTTP_200_OK,
    )

@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAdminUser])
def api_mark_all_notifications_read(request):
    notifications = AdminNotification.objects.filter(
        Q(created_for=request.user) | Q(created_for__isnull=True)
    )

    AdminNotificationRead.objects.bulk_create(
        [
            AdminNotificationRead(
                user=request.user,
                notification=notification,
            )
            for notification in notifications
        ],
        ignore_conflicts=True,
    )

    return Response(
        {"success": True},
        status=status.HTTP_200_OK,
    )

# =====================================================
# DJANGO ADMIN AJAX VIEWS - FOR CUSTOM ADMIN HEADER
# =====================================================

@staff_member_required
def admin_notification_dropdown(request):
    read_subquery = AdminNotificationRead.objects.filter(
        user=request.user,
        notification=OuterRef("pk"),
    )

    queryset = AdminNotification.objects.filter(
        Q(created_for=request.user) | Q(created_for__isnull=True)
    ).annotate(
        is_read=Exists(read_subquery)
    )

    unread_notifications = queryset.filter(
        is_read=False
    ).order_by("-created_at")[:10]

    data = [
        {
            "id": notification.id,
            "title": notification.title,
            "message": notification.message,
            "type": notification.notification_type,
            "url": notification.url or "#",
            "created_at": localtime(notification.created_at).strftime(
                "%d %b, %I:%M %p"
            ),
        }
        for notification in unread_notifications
    ]

    unread_count = queryset.filter(
        is_read=False
    ).count()

    return JsonResponse(
        {
            "count": unread_count,
            "notifications": data,
        }
    )

@staff_member_required
@require_POST
def admin_mark_notification_read(request, pk):
    notification = get_object_or_404(
        AdminNotification,
        Q(created_for=request.user) | Q(created_for__isnull=True),
        pk=pk,
    )

    AdminNotificationRead.objects.get_or_create(
        user=request.user,
        notification=notification,
    )

    return JsonResponse({"success": True})

@staff_member_required
@require_POST
def admin_mark_all_notifications_read(request):
    notifications = AdminNotification.objects.filter(
        Q(created_for=request.user) | Q(created_for__isnull=True)
    )

    AdminNotificationRead.objects.bulk_create(
        [
            AdminNotificationRead(
                user=request.user,
                notification=notification,
            )
            for notification in notifications
        ],
        ignore_conflicts=True,
    )

    return JsonResponse({"success": True})