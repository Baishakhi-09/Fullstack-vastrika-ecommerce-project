from django.db import models


# -------------------- SALES REPORT -------------------- #
class SalesReport(models.Model):
    report_date = models.DateField(unique=True)

    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_orders = models.PositiveIntegerField(default=0)
    total_customers = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-report_date"]
        indexes = [
            models.Index(fields=["report_date"]),
        ]
        verbose_name = "Sales Report"
        verbose_name_plural = "Sales Reports"

    def __str__(self):
        return f"Sales Report - {self.report_date}"


# -------------------- PRODUCT REPORT -------------------- #
class ProductReport(models.Model):
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="reports",
        db_index=True,
    )

    report_date = models.DateField()

    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_quantity = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-report_date"]
        indexes = [
            models.Index(fields=["product", "report_date"]),
            models.Index(fields=["report_date"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["product", "report_date"],
                name="unique_product_report_per_day",
            )
        ]
        verbose_name = "Product Report"
        verbose_name_plural = "Product Reports"

    def __str__(self):
        return f"{self.product} Report ({self.report_date})"


# -------------------- CUSTOMER REPORT -------------------- #
class CustomerReport(models.Model):
    customer = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="reports",
        db_index=True,
    )

    report_date = models.DateField()

    total_orders = models.PositiveIntegerField(default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-report_date"]
        indexes = [
            models.Index(fields=["customer", "report_date"]),
            models.Index(fields=["report_date"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["customer", "report_date"],
                name="unique_customer_report_per_day",
            )
        ]
        verbose_name = "Customer Report"
        verbose_name_plural = "Customer Reports"

    def __str__(self):
        return f"{self.customer} Report ({self.report_date})"