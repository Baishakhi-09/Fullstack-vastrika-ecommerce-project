from __future__ import annotations

from django.contrib import admin
from django.http import HttpRequest
from django.utils.html import (
    format_html,
)

from apps.orders.models import (
    Payment,
)

from vastrika_backend.admin_site import (
    admin_site,
)


# =========================================================
# PAYMENT ADMIN
# =========================================================
@admin.register(
    Payment,
    site=admin_site,
)
class PaymentAdmin(
    admin.ModelAdmin,
):
    list_display = (
        "id",
        "order",
        "payment_status_badge",
        "amount",
        "payment_method",
        "created_at",
    )

    search_fields = (
        "order__order_number",
        "order__id",
    )

    list_filter = (
        "status",
        "payment_method",
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
        "order",
    )

    list_display_links = (
        "id",
        "order",
    )

    autocomplete_fields = (
        "order",
    )

    readonly_fields = (
        "order",
        "amount",
        "status",
        "payment_method",
        "created_at",
    )

    fieldsets = (
        (
            "Payment Information",
            {
                "fields": (
                    "order",
                    "amount",
                    "status",
                    "payment_method",
                    "created_at",
                )
            },
        ),
    )

    # STATUS BADGE
    @admin.display(
        description="Status",
        ordering="status",
    )
    def payment_status_badge(
        self,
        obj: Payment,
    ) -> str:
        styles = {
            "pending": (
                "Pending",
                "#f59e0b",
            ),
            "paid": (
                "Paid",
                "#16a34a",
            ),
            "failed": (
                "Failed",
                "#dc2626",
            ),
            "refunded": (
                "Refunded",
                "#2563eb",
            ),
            "cancelled": (
                "Cancelled",
                "#6b7280",
            ),
        }

        label, color = styles.get(
            obj.status,
            (
                "Unknown",
                "#6b7280",
            ),
        )

        return format_html(
            """
            <span
                style="
                    display:inline-flex;
                    align-items:center;
                    gap:7px;
                    background:{};
                    color:white;
                    padding:5px 12px;
                    border-radius:999px;
                    font-size:12px;
                    font-weight:700;
                "
            >
                <span
                    style="
                        width:7px;
                        height:7px;
                        border-radius:50%;
                        background:white;
                        display:inline-block;
                    "
                ></span>

                <span>{}</span>
            </span>
            """,
            color,
            label,
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
        obj: Payment | None = None,
    ) -> bool:
        return False

    def has_delete_permission(
        self,
        request: HttpRequest,
        obj: Payment | None = None,
    ) -> bool:
        return False

    def has_view_permission(
        self,
        request: HttpRequest,
        obj: Payment | None = None,
    ) -> bool:
        return bool(
            request.user.is_authenticated
            and request.user.is_staff
        )