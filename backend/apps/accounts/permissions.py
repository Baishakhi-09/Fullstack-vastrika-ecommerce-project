from __future__ import annotations

from typing import Any

from rest_framework.permissions import BasePermission

from .models import User


# =========================================================
# BASE ROLE PERMISSION
# =========================================================
class BaseRolePermission(BasePermission):
    allowed_roles: list[str] = []

    def has_permission(
        self,
        request: Any,
        view: Any,
    ) -> bool:
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and getattr(user, "role", None)
            in self.allowed_roles
        )

    def has_object_permission(
        self,
        request: Any,
        view: Any,
        obj: Any,
    ) -> bool:
        return self.has_permission(
            request,
            view,
        )


# =========================================================
# ADMIN PERMISSION
# =========================================================
class IsAdminRole(BaseRolePermission):
    allowed_roles = [
        User.Role.ADMIN,
    ]


# =========================================================
# MANAGER PERMISSION
# =========================================================
class IsManagerRole(BaseRolePermission):
    """
    Allow access to admins and managers.
    """

    allowed_roles = [
        User.Role.ADMIN,
        User.Role.MANAGER,
    ]


# =========================================================
# EDITOR PERMISSION
# =========================================================
class IsEditorRole(BaseRolePermission):
    """
    Allow access to admins, managers, and editors.
    """

    allowed_roles = [
        User.Role.ADMIN,
        User.Role.MANAGER,
        User.Role.EDITOR,
    ]


# =========================================================
# USER PERMISSION
# =========================================================
class IsUserRole(BaseRolePermission):
    """
    Allow access only to regular users.
    """

    allowed_roles = [
        User.Role.USER,
    ]


# =========================================================
# OWNER OR ADMIN PERMISSION
# =========================================================
class IsOwnerOrAdmin(BasePermission):
    def has_permission(
        self,
        request: Any,
        view: Any,
    ) -> bool:
        """
        Allow only authenticated users.
        """

        user = request.user

        return bool(
            user
            and user.is_authenticated
        )

    def has_object_permission(
        self,
        request: Any,
        view: Any,
        obj: Any,
    ) -> bool:
        """
        Validate ownership or admin access.
        """

        user = request.user

        if not (
            user
            and user.is_authenticated
        ):
            return False

        if getattr(user, "role", None) == User.Role.ADMIN:
            return True

        if obj == user:
            return True

        if getattr(obj, "user", None) == user:
            return True

        return False