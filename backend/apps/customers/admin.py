from __future__ import annotations

from django.contrib import admin
from django.http import HttpRequest

from apps.customers.models import (
    Customer,
)

from vastrika_backend.admin_site import (
    admin_site,
)


# =========================================================
# CUSTOMER ADMIN
# =========================================================
@admin.register(
    Customer,
    site=admin_site,
)
class CustomerAdmin(
    admin.ModelAdmin,
):
    list_display = (
        "id",
        "user",
        "phone",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "phone",
    )

    list_filter = (
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
        "user",
    )

    list_display_links = (
        "id",
        "user",
    )

    autocomplete_fields = (
        "user",
    )

    readonly_fields = (
        "created_at",
    )

    # PERMISSIONS
    def has_delete_permission(
        self,
        request: HttpRequest,
        obj=None,
    ) -> bool:
        return bool(
            request.user.is_superuser
        )