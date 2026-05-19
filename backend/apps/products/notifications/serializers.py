from __future__ import annotations

from django.db.models import (
    Exists,
    OuterRef,
    QuerySet,
)

from rest_framework import (
    serializers,
)

from apps.products.notifications.models import (
    AdminNotification,
    AdminNotificationRead,
)


# =========================================================
# ADMIN NOTIFICATION SERIALIZER
# =========================================================
class AdminNotificationSerializer(
    serializers.ModelSerializer,
):
    is_read = (
        serializers.SerializerMethodField()
    )

    class Meta:
        model = AdminNotification

        fields = (
            "id",
            "title",
            "message",
            "notification_type",
            "url",
            "is_read",
            "created_at",
        )

        read_only_fields = (
            "id",
            "title",
            "message",
            "notification_type",
            "url",
            "is_read",
            "created_at",
        )

    def get_is_read(
        self,
        obj: AdminNotification,
    ) -> bool:
        request = self.context.get(
            "request",
        )

        if not request:
            return False

        user = getattr(
            request,
            "user",
            None,
        )

        if not (
            user
            and user.is_authenticated
        ):
            return False

        # USE ANNOTATED VALUE
        annotated_value = getattr(
            obj,
            "is_read",
            None,
        )

        if annotated_value is not None:
            return bool(
                annotated_value
            )

        # FALLBACK QUERY
        return (
            AdminNotificationRead.objects.filter(
                user=user,
                notification=obj,
            ).exists()
        )

    # QUERYSET OPTIMIZATION
    @staticmethod
    def setup_eager_loading(
        queryset: QuerySet,
        user,
    ) -> QuerySet:
        if not (
            user
            and user.is_authenticated
        ):
            return queryset

        read_subquery = (
            AdminNotificationRead.objects.filter(
                user=user,
                notification=OuterRef("pk"),
            )
        )

        return queryset.annotate(
            is_read=Exists(
                read_subquery,
            )
        )