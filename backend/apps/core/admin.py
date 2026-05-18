from __future__ import annotations

from django.contrib import admin
from django.http import HttpRequest

from apps.accounts.models import User
from apps.core.models import AuditLog

from vastrika_backend.admin_site import (
    admin_site,
)


# AUDIT LOG ADMIN
@admin.register(
    AuditLog,
    site=admin_site,
)
class AuditLogAdmin(
    admin.ModelAdmin,
):
    list_display = (
        "id",
        "actor",
        "action",
        "content_type",
        "object_repr",
        "created_at",
    )

    list_filter = (
        "action",
        "content_type",
        "created_at",
    )

    search_fields = (
        "actor__email",
        "actor__username",
        "object_repr",
    )

    ordering = (
        "-created_at",
    )

    date_hierarchy = "created_at"

    list_per_page = 50

    list_select_related = (
        "actor",
    )

    # READ-ONLY CONFIGURATION
    readonly_fields = tuple(
        field.name
        for field
        in AuditLog._meta.concrete_fields
    ) + tuple(
        field.name
        for field
        in AuditLog._meta.many_to_many
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
        obj: AuditLog | None = None,
    ) -> bool:
        return False

    def has_delete_permission(
        self,
        request: HttpRequest,
        obj: AuditLog | None = None,
    ) -> bool:
        user = request.user

        return bool(
            user.is_authenticated
            and (
                user.is_superuser
                or getattr(
                    user,
                    "role",
                    None,
                )
                == User.Role.ADMIN
            )
        )

    def has_view_permission(
        self,
        request: HttpRequest,
        obj: AuditLog | None = None,
    ) -> bool:
        user = request.user

        return bool(
            user.is_authenticated
            and user.is_staff
        )