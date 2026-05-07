from django.contrib import admin

from vastrika_backend.admin_site import admin_site
from apps.core.models import AuditLog


@admin.register(AuditLog, site=admin_site)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "actor",
        "action",
        "content_type",
        "object_repr",
        "created_at",
    )

    search_fields = (
        "actor__email",
        "actor__username",
        "object_repr",
    )

    list_filter = (
        "action",
        "content_type",
        "created_at",
    )

    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    readonly_fields = [f.name for f in AuditLog._meta.concrete_fields] + [
        f.name for f in AuditLog._meta.many_to_many
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or getattr(request.user, "role", None) == "admin"