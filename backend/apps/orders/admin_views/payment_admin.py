from django.contrib import admin

from vastrika_backend.admin_site import admin_site
from apps.orders.models import Payment


@admin.register(Payment, site=admin_site)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "amount", "status", "payment_method", "created_at")
    search_fields = ("order__order_number", "order__id")
    list_filter = ("status", "payment_method", "created_at")
    ordering = ("-created_at",)
    list_select_related = ("order",)
    readonly_fields = ("created_at",)