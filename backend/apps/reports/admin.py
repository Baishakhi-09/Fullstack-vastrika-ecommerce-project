from __future__ import annotations

from django.contrib import admin
from django.http import HttpRequest
from django.utils.html import format_html

from apps.reports.models import (
    CustomerReport,
    ProductReport,
    SalesReport,
)

from vastrika_backend.admin_site import (
    admin_site,
)


# =========================================================
# BASE REPORT ADMIN
# =========================================================
class BaseReportAdmin(
    admin.ModelAdmin,
):
    """
    Base admin configuration
    for all report models.
    """

    list_per_page = 50

    save_on_top = True

    actions = None

    # READONLY FIELDS
    def get_readonly_fields(
        self,
        request: HttpRequest,
        obj=None,
    ) -> tuple[str, ...]:

        return tuple(
            field.name
            for field
            in self.model._meta.fields
        )

    # DISABLE ADD
    def has_add_permission(
        self,
        request: HttpRequest,
    ) -> bool:
        return False

    # DISABLE DELETE
    def has_delete_permission(
        self,
        request: HttpRequest,
        obj=None,
    ) -> bool:
        return False

    # DISABLE EDITING
    def has_change_permission(
        self,
        request: HttpRequest,
        obj=None,
    ) -> bool:

        # ALLOW VIEW PAGE ACCESS
        if request.method in ["GET", "HEAD"]:
            return True

        return False


# =========================================================
# SALES REPORT ADMIN
# =========================================================
@admin.register(
    SalesReport,
    site=admin_site,
)
class SalesReportAdmin(
    BaseReportAdmin,
):
    list_display = (
        "id",
        "formatted_total_sales",
        "total_orders",
        "report_date",
    )

    list_filter = (
        "report_date",
    )

    search_fields = (
        "id",
    )

    ordering = (
        "-report_date",
    )

    date_hierarchy = (
        "report_date"
    )

    # SALES FORMATTER
    @admin.display(
        description="Total Sales",
        ordering="total_sales",
    )
    def formatted_total_sales(
        self,
        obj: SalesReport,
    ) -> str:

        return format_html(
            (
                "<span "
                "style='"
                "font-weight:700;"
                "color:#16a34a;"
                "'>"
                "₹ {}"
                "</span>"
            ),
            obj.total_sales,
        )


# =========================================================
# PRODUCT REPORT ADMIN
# =========================================================
@admin.register(
    ProductReport,
    site=admin_site,
)
class ProductReportAdmin(
    BaseReportAdmin,
):
    list_display = (
        "id",
        "product",
        "formatted_total_sales",
        "total_quantity",
    )

    list_filter = (
        "product",
    )

    search_fields = (
        "product__name",
        "product__sku",
    )

    ordering = (
        "-total_sales",
    )

    list_select_related = (
        "product",
    )

    autocomplete_fields = (
        "product",
    )

    # SALES FORMATTER
    @admin.display(
        description="Total Sales",
        ordering="total_sales",
    )
    def formatted_total_sales(
        self,
        obj: ProductReport,
    ) -> str:

        return format_html(
            (
                "<span "
                "style='"
                "font-weight:700;"
                "color:#2563eb;"
                "'>"
                "₹ {}"
                "</span>"
            ),
            obj.total_sales,
        )


# =========================================================
# CUSTOMER REPORT ADMIN
# =========================================================
@admin.register(
    CustomerReport,
    site=admin_site,
)
class CustomerReportAdmin(
    BaseReportAdmin,
):
    list_display = (
        "id",
        "customer",
        "total_orders",
        "formatted_total_spent",
    )

    list_filter = (
        "customer",
    )

    search_fields = (
        "customer__email",
        "customer__first_name",
        "customer__last_name",
    )

    ordering = (
        "-total_spent",
    )

    list_select_related = (
        "customer",
    )

    autocomplete_fields = (
        "customer",
    )

    # SPENT FORMATTER
    @admin.display(
        description="Total Spent",
        ordering="total_spent",
    )
    def formatted_total_spent(
        self,
        obj: CustomerReport,
    ) -> str:
        return format_html(
            (
                "<span "
                "style='"
                "font-weight:700;"
                "color:#dc2626;"
                "'>"
                "₹ {}"
                "</span>"
            ),
            obj.total_spent,
        )