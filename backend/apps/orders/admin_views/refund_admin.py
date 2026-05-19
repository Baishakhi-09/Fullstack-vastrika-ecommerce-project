from __future__ import annotations

from django.contrib import admin
from django.http import HttpRequest
from django.utils.html import (
    format_html,
)

from apps.orders.models import (
    Refund,
)

from vastrika_backend.admin_site import (
    admin_site,
)


# =========================================================
# REFUND ADMIN
# =========================================================
@admin.register(
    Refund,
    site=admin_site,
)
class RefundAdmin(
    admin.ModelAdmin,
):
    list_display = (
        "id",
        "order",
        "refund_status_badge",
        "amount",
        "created_at",
    )

    list_display_links = (
        "id",
        "order",
    )

    search_fields = (
        "order__order_number",
        "order__id",
    )

    list_filter = (
        "status",
        "created_at",
        "order",
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

    autocomplete_fields = (
        "order",
    )

    # READONLY CONFIGURATION
    readonly_fields = (
        "order",
        "amount",
        "status",
        "created_at",
    )

    fieldsets = (
        (
            "Refund Information",
            {
                "fields": (
                    "order",
                    "amount",
                    "status",
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
    def refund_status_badge(
        self,
        obj: Refund,
    ) -> str:
        styles = {
            "pending": (
                "Pending",
                "#f59e0b",
            ),
            "approved": (
                "Approved",
                "#2563eb",
            ),
            "processed": (
                "Processed",
                "#16a34a",
            ),
            "failed": (
                "Failed",
                "#dc2626",
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
        obj: Refund | None = None,
    ) -> bool:
        return False

    def has_delete_permission(
        self,
        request: HttpRequest,
        obj: Refund | None = None,
    ) -> bool:
        return False

    def has_view_permission(
        self,
        request: HttpRequest,
        obj: Refund | None = None,
    ) -> bool:
        return bool(
            request.user.is_authenticated
            and request.user.is_staff
        )