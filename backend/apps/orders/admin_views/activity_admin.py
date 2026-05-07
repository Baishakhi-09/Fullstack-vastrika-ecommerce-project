from django.contrib import admin

from vastrika_backend.admin_site import admin_site
from apps.orders.audit_models import OrderActivityLog


@admin.register(OrderActivityLog, site=admin_site)
class OrderActivityLogAdmin(admin.ModelAdmin):
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

    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_select_related = ("order", "actor")

    readonly_fields = (
        "order",
        "actor",
        "action",
        "message",
        "old_status",
        "new_status",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return getattr(request.user, "role", None) == "admin"