from __future__ import annotations

from django.db import (
    models,
)
from django.db.models import (
    Q,
)


# =========================================================
# BASE REPORT MODEL
# =========================================================
class BaseReportModel(
    models.Model,
):
    """
    Abstract base model for
    all reporting models.
    """

    report_date = models.DateField(
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        abstract = True


# =========================================================
# SALES REPORT
# =========================================================
class SalesReport(
    BaseReportModel,
):
    total_sales = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    total_orders = (
        models.PositiveIntegerField(
            default=0,
        )
    )

    total_customers = (
        models.PositiveIntegerField(
            default=0,
        )
    )

    class Meta:
        db_table = (
            "reports_sales_report"
        )

        ordering = [
            "-report_date",
        ]

        indexes = [
            models.Index(
                fields=[
                    "report_date",
                ]
            ),
        ]

        constraints = [
            models.CheckConstraint(
                check=Q(
                    total_sales__gte=0
                ),
                name=(
                    "sales_report_total_"
                    "sales_gte_0"
                ),
            ),
            models.CheckConstraint(
                check=Q(
                    total_orders__gte=0
                ),
                name=(
                    "sales_report_total_"
                    "orders_gte_0"
                ),
            ),
            models.CheckConstraint(
                check=Q(
                    total_customers__gte=0
                ),
                name=(
                    "sales_report_total_"
                    "customers_gte_0"
                ),
            ),
            models.UniqueConstraint(
                fields=[
                    "report_date",
                ],
                name=(
                    "unique_sales_"
                    "report_per_day"
                ),
            ),
        ]

        verbose_name = (
            "Sales Report"
        )

        verbose_name_plural = (
            "Sales Reports"
        )

    def __str__(
        self,
    ) -> str:
        return (
            f"Sales Report - "
            f"{self.report_date}"
        )


# =========================================================
# PRODUCT REPORT
# =========================================================
class ProductReport(
    BaseReportModel,
):
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name=(
            "product_reports"
        ),
        db_index=True,
    )

    total_sales = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    total_quantity = (
        models.PositiveIntegerField(
            default=0,
        )
    )

    class Meta:
        db_table = (
            "reports_product_report"
        )

        ordering = [
            "-report_date",
        ]

        indexes = [
            models.Index(
                fields=[
                    "product",
                    "report_date",
                ]
            ),
            models.Index(
                fields=[
                    "report_date",
                ]
            ),
        ]

        constraints = [
            models.CheckConstraint(
                check=Q(
                    total_sales__gte=0
                ),
                name=(
                    "product_report_total_"
                    "sales_gte_0"
                ),
            ),
            models.CheckConstraint(
                check=Q(
                    total_quantity__gte=0
                ),
                name=(
                    "product_report_total_"
                    "quantity_gte_0"
                ),
            ),
            models.UniqueConstraint(
                fields=[
                    "product",
                    "report_date",
                ],
                name=(
                    "unique_product_"
                    "report_per_day"
                ),
            ),
        ]

        verbose_name = (
            "Product Report"
        )

        verbose_name_plural = (
            "Product Reports"
        )

    def __str__(
        self,
    ) -> str:
        return (
            f"{self.product.name} "
            f"Report "
            f"({self.report_date})"
        )


# =========================================================
# CUSTOMER REPORT
# =========================================================
class CustomerReport(
    BaseReportModel,
):
    customer = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        related_name=(
            "customer_reports"
        ),
        db_index=True,
    )

    total_orders = (
        models.PositiveIntegerField(
            default=0,
        )
    )

    total_spent = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    class Meta:
        db_table = (
            "reports_customer_report"
        )

        ordering = [
            "-report_date",
        ]

        indexes = [
            models.Index(
                fields=[
                    "customer",
                    "report_date",
                ]
            ),
            models.Index(
                fields=[
                    "report_date",
                ]
            ),
        ]

        constraints = [
            models.CheckConstraint(
                check=Q(
                    total_orders__gte=0
                ),
                name=(
                    "customer_report_total_"
                    "orders_gte_0"
                ),
            ),
            models.CheckConstraint(
                check=Q(
                    total_spent__gte=0
                ),
                name=(
                    "customer_report_total_"
                    "spent_gte_0"
                ),
            ),
            models.UniqueConstraint(
                fields=[
                    "customer",
                    "report_date",
                ],
                name=(
                    "unique_customer_"
                    "report_per_day"
                ),
            ),
        ]

        verbose_name = (
            "Customer Report"
        )

        verbose_name_plural = (
            "Customer Reports"
        )

    def __str__(
        self,
    ) -> str:
        return (
            f"{self.customer.email} "
            f"Report "
            f"({self.report_date})"
        )