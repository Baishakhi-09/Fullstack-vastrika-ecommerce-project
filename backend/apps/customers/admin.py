from django.contrib import admin
from vastrika_backend.admin_site import admin_site
from .models import Customer, Review


@admin.register(Customer, site=admin_site)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "phone", "created_at")
    search_fields = ("user__username", "user__email", "phone")
    list_filter = ("created_at",)
    ordering = ("-created_at",)

    list_select_related = ("user",)
    readonly_fields = ("created_at",)


@admin.register(Review, site=admin_site)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "product", "rating", "created_at")
    search_fields = ("customer__username", "customer__email", "product__name")
    list_filter = ("rating", "created_at")
    ordering = ("-created_at",)

    list_select_related = ("customer", "product")
    readonly_fields = ("created_at",)