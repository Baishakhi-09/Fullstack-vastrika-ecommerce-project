# backend/apps/accounts/permissions.py

from types import MappingProxyType

from rest_framework.permissions import BasePermission

from .constants import UserRole


def get_user_role(user):
    """
    Centralized user role lookup.

    This allows future flexibility if roles move to:
    - profile models
    - groups
    - JWT claims
    - external RBAC services
    """

    return getattr(user, "role", None)


def is_authenticated_user(user):
    """
    Check whether the user is authenticated.
    """

    return bool(
        user and user.is_authenticated
    )


ROLE_HIERARCHY = MappingProxyType({
    UserRole.ADMIN: 100,
    UserRole.MANAGER: 80,
    UserRole.EDITOR: 60,
    UserRole.USER: 20,
})


class RolePermission(BasePermission):
    """
    Base permission class with hierarchical role support.
    """

    allowed_roles = ()

    message = (
        "You do not have permission "
        "to perform this action."
    )

    def has_permission(
        self,
        request,
        view,
    ):
        user = request.user

        if not is_authenticated_user(user):
            return False

        user_role = get_user_role(user)

        if not user_role:
            return False

        user_level = ROLE_HIERARCHY.get(
            user_role,
            0,
        )

        return any(
            user_level >= ROLE_HIERARCHY.get(
                role,
                0,
            )
            for role in self.allowed_roles
        )

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        return self.has_permission(
            request,
            view,
        )


class IsAdminRole(RolePermission):
    allowed_roles = (
        UserRole.ADMIN,
    )


class IsManagerRole(RolePermission):
    allowed_roles = (
        UserRole.MANAGER,
    )


class IsEditorRole(RolePermission):
    allowed_roles = (
        UserRole.EDITOR,
    )


class IsCustomerRole(RolePermission):
    allowed_roles = (
        UserRole.USER,
    )


class IsOwnerOrAdmin(BasePermission):
    """
    Allow access to object owners or admins.
    """

    owner_fields = (
        "user",
        "owner",
        "created_by",
        "author",
    )

    message = (
        "You do not have permission "
        "to access this object."
    )

    def has_permission(
        self,
        request,
        view,
    ):
        return is_authenticated_user(
            request.user,
        )

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        user = request.user

        if not is_authenticated_user(user):
            return False

        if (
            get_user_role(user)
            == UserRole.ADMIN
        ):
            return True

        if obj == user:
            return True

        return any(
            getattr(obj, field, None) == user
            for field in self.owner_fields
        )