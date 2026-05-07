from django.contrib import admin
from vastrika_backend.admin_site import admin_site
from .models import SalesReport, ProductReport, CustomerReport


# -------------------- SALES REPORT -------------------- #
@admin.register(SalesReport, site=admin_site)
class SalesReportAdmin(admin.ModelAdmin):
    list_display = ("id", "total_sales", "total_orders", "report_date")
    list_filter = ("report_date",)
    search_fields = ("id",)
    ordering = ("-report_date",)
    readonly_fields = [field.name for field in SalesReport._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# -------------------- PRODUCT REPORT -------------------- #
@admin.register(ProductReport, site=admin_site)
class ProductReportAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "total_sales", "total_quantity")
    list_filter = ("product",)
    search_fields = ("product__name",)
    ordering = ("-total_sales",)
    readonly_fields = [field.name for field in ProductReport._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# -------------------- CUSTOMER REPORT -------------------- #
@admin.register(CustomerReport, site=admin_site)
class CustomerReportAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "total_orders", "total_spent")
    list_filter = ("customer",)
    search_fields = ("customer__email",)
    ordering = ("-total_spent",)
    readonly_fields = [field.name for field in CustomerReport._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False