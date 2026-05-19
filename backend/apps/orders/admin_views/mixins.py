from __future__ import annotations

from typing import Any

from django.contrib.admin import ModelAdmin
from django.http import HttpRequest

from apps.accounts.models import (
    User,
)


# =========================================================
# ROLE-BASED ORDER ADMIN MIXIN
# =========================================================
class RoleBasedOrderAdminMixin(
    ModelAdmin,
):
    # ROLE CONFIGURATION
    ADMIN_ROLES = (
        User.Role.ADMIN,
    )

    MANAGER_ROLES = (
        User.Role.ADMIN,
        User.Role.MANAGER,
    )

    EDITOR_ROLES = (
        User.Role.ADMIN,
        User.Role.MANAGER,
        User.Role.EDITOR,
    )

    # FIELD RESTRICTIONS
    EDITOR_HIDDEN_FIELDS = (
        "total_amount",
        "paid_at",
        "refunded_at",
    )

    MANAGER_READONLY_FIELDS = (
        "total_amount",
    )

    # ROLE HELPERS
    def get_user_role(
        self,
        request: HttpRequest,
    ) -> str | None:
        """
        Resolve authenticated user role.
        """

        user = request.user

        if not (
            user.is_authenticated
            and user.is_active
            and user.is_staff
        ):
            return None

        if user.is_superuser:
            return User.Role.ADMIN

        return getattr(
            user,
            "role",
            None,
        )

    def has_role_access(
        self,
        request: HttpRequest,
        allowed_roles: tuple[str, ...],
    ) -> bool:
        """
        Validate role-based access.
        """

        user_role = self.get_user_role(
            request,
        )

        return bool(
            user_role
            and user_role
            in allowed_roles
        )

    # PERMISSIONS
    def has_view_permission(
        self,
        request: HttpRequest,
        obj: Any | None = None,
    ) -> bool:
        """
        Allow dashboard viewing
        for editor-level roles.
        """

        return self.has_role_access(
            request,
            self.EDITOR_ROLES,
        )

    def has_add_permission(
        self,
        request: HttpRequest,
    ) -> bool:
        """
        Allow object creation
        for manager-level roles.
        """

        return self.has_role_access(
            request,
            self.MANAGER_ROLES,
        )

    def has_change_permission(
        self,
        request: HttpRequest,
        obj: Any | None = None,
    ) -> bool:
        """
        Allow object modification
        for manager-level roles.
        """

        return self.has_role_access(
            request,
            self.MANAGER_ROLES,
        )

    def has_delete_permission(
        self,
        request: HttpRequest,
        obj: Any | None = None,
    ) -> bool:
        """
        Restrict deletion
        to administrator roles.
        """

        return self.has_role_access(
            request,
            self.ADMIN_ROLES,
        )

    # DYNAMIC FIELD VISIBILITY
    def get_fields(
        self,
        request: HttpRequest,
        obj: Any | None = None,
    ) -> list[str]:
        """
        Dynamically filter fields
        based on role permissions.
        """

        fields = list(
            super().get_fields(
                request,
                obj,
            )
        )

        user_role = self.get_user_role(
            request,
        )

        if (
            user_role
            == User.Role.EDITOR
        ):
            fields = [
                field
                for field in fields
                if field
                not in self.EDITOR_HIDDEN_FIELDS
            ]

        return fields

    # READONLY FIELD CONTROL
    def get_readonly_fields(
        self,
        request: HttpRequest,
        obj: Any | None = None,
    ) -> tuple[str, ...]:
        """
        Dynamically apply readonly fields
        based on user role.
        """

        readonly_fields = list(
            super().get_readonly_fields(
                request,
                obj,
            )
        )

        user_role = self.get_user_role(
            request,
        )

        if (
            user_role
            == User.Role.MANAGER
        ):
            readonly_fields.extend(
                self.MANAGER_READONLY_FIELDS
            )

        return tuple(
            set(readonly_fields)
        )