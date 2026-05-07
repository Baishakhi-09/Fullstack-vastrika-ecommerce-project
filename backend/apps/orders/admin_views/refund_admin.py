from django.contrib import admin

from vastrika_backend.admin_site import admin_site
from apps.orders.models import Refund


@admin.register(Refund, site=admin_site)
class RefundAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "amount", "status", "created_at")
    list_display_links = ("id", "order")
    search_fields = ("order__order_number", "order__id")
    list_filter = ("status", "created_at", "order")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_select_related = ("order",)
    readonly_fields = ("created_at",)