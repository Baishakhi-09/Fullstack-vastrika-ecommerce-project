from __future__ import annotations

from django.contrib import admin
from django.http import HttpRequest

from apps.orders.audit_models import (
    OrderActivityLog,
)

from vastrika_backend.admin_site import (
    admin_site,
)


# =========================================================
# ORDER ACTIVITY LOG ADMIN
# =========================================================
@admin.register(
    OrderActivityLog,
    site=admin_site,
)
class OrderActivityLogAdmin(
    admin.ModelAdmin,
):
    list_display = (
        "id",
        "order",
        "actor",
        "action",
        "old_status",
        "new_status",
        "created_at",
    )

    search_fields = (
        "order__order_number",
        "actor__email",
        "actor__username",
        "message",
    )

    list_filter = (
        "action",
        "created_at",
    )

    ordering = (
        "-created_at",
    )

    date_hierarchy = (
        "created_at"
    )

    list_per_page = 50

    list_select_related = (
        "order",
        "actor",
    )

    list_display_links = (
        "id",
        "order",
    )

    autocomplete_fields = (
        "order",
        "actor",
    )

    readonly_fields = (
        "order",
        "actor",
        "action",
        "message",
        "old_status",
        "new_status",
        "created_at",
    )

    # PERMISSIONS
    def has_add_permission(
        self,
        request: HttpRequest,
    ) -> bool:
        return False

    def has_change_permission(
        self,
        request: HttpRequest,
        obj: OrderActivityLog | None = None,
    ) -> bool:
        return False

    def has_delete_permission(
        self,
        request: HttpRequest,
        obj: OrderActivityLog | None = None,
    ) -> bool:
        return False

    def has_view_permission(
        self,
        request: HttpRequest,
        obj: OrderActivityLog | None = None,
    ) -> bool:
        return bool(
            request.user.is_authenticated
            and request.user.is_staff
        )