from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user and user.is_authenticated and getattr(user, "role", None) == "admin"

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsManagerRole(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user and user.is_authenticated and getattr(user, "role", None) in ["admin", "manager"]

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsEditorRole(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user and user.is_authenticated and getattr(user, "role", None) in ["admin", "manager", "editor"]

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsCustomerRole(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user and user.is_authenticated and getattr(user, "role", None) == "user"

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user and user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        return (
            user
            and user.is_authenticated
            and (
                getattr(user, "role", None) == "admin"
                or obj == user
                or getattr(obj, "user", None) == user
            )
        )