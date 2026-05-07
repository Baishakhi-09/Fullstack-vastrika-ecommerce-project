from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin

from vastrika_backend.admin_site import admin_site
from .models import User, NewsletterSubscriber

# Register your models here.

class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "role",
        "profile_preview",
        "is_staff",
        "is_superuser",
        "is_active",
    )

    list_filter = (
        "role",
        "is_staff",
        "is_superuser",
        "is_active",
    )

    search_fields = (
        "username",
        "email",
        "phone",
    )

    readonly_fields = ("profile_preview",)

    fieldsets = UserAdmin.fieldsets + (
        ("Profile Details", {
            "fields": (
                "profile_preview",
                "profile_image",
                "phone",
                "alternate_phone",
                "gender",
                "role",
            )
        }),
        ("Address Details", {
            "fields": (
                "address",
                "address_line_1",
                "address_line_2",
                "city",
                "state",
                "pincode",
                "country",
            )
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Extra Details", {
            "fields": (
                "email",
                "phone",
                "role",
                "profile_image",
            )
        }),
    )

    def profile_preview(self, obj):
        if obj and obj.profile_image:
            return format_html(
                '<img src="{}" style="width:42px;height:42px;border-radius:50%;object-fit:cover;" />',
                obj.profile_image.url,
            )
        return "No Image"
    
    profile_preview.short_description = "Profile"

# ---------- Newsletter ---------- #
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "subscribed_at", "updated_at")
    search_fields = ("email",)
    list_filter = ("is_active", "subscribed_at")
    readonly_fields = ("subscribed_at", "updated_at")

admin_site.register(User, CustomUserAdmin)
admin_site.register(NewsletterSubscriber, NewsletterSubscriberAdmin)