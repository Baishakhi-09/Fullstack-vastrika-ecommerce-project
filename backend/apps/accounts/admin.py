from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from vastrika_backend.admin_site import admin_site

from .models import (
    User,
    NewsletterSubscriber,
)

# Register your models here.

class CustomUserAdmin(UserAdmin):
    """
    Custom admin configuration for User model.
    """

    list_select_related = True

    save_on_top = True
    actions_on_top = True
    actions_on_bottom = True

    list_display = (
        "username",
        "email",
        "role",
        "profile_preview",
        "is_staff",
        "is_superuser",
        "is_active",
    )

    list_display_links = (
        "username",
        "email",
    )

    list_filter = (
        "role",
        "is_staff",
        "is_superuser",
        "is_active",
    )

    search_fields = (
        "^username",
        "^email",
        "^phone",
    )

    search_help_text = (
        "Search by username, email, or phone."
    )

    readonly_fields = (
        "profile_preview",
    )

    ordering = (
        "-id",
    )

    list_per_page = 25

    show_full_result_count = False

    empty_value_display = "—"

    fieldsets = UserAdmin.fieldsets + (
        (
            "Profile Details",
            {
                "fields": (
                    "profile_preview",
                    "profile_image",
                    "phone",
                    "alternate_phone",
                    "gender",
                    "role",
                ),
            },
        ),
        (
            "Address Details",
            {
                "fields": (
                    "address",
                    "address_line_1",
                    "address_line_2",
                    "city",
                    "state",
                    "pincode",
                    "country",
                ),
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Extra Details",
            {
                "fields": (
                    "email",
                    "phone",
                    "role",
                    "profile_image",
                ),
            },
        ),
    )

    @admin.display(description="Profile")
    def profile_preview(
        self,
        obj: User,
    ) -> str:
        if obj and obj.profile_image:
            return format_html(
                """
                <img src="{}" style="width:42px;height:42px;border-radius:50%;object-fit:cover;" />
                """,
                obj.profile_image.url,
            )
        return self.empty_value_display

# ---------- Newsletter ---------- #
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    """
    Admin configuration for newsletter subscribers.
    """

    save_on_top = True
    actions_on_top = True
    actions_on_bottom = True
    date_hierarchy = "subscribed_at"

    list_display = (
        "email",
        "is_active",
        "subscribed_at",
        "updated_at",
    )
    list_display_links = (
        "email",
    )

    list_editable = (
        "is_active",
    )
    search_fields = (
        "^email",
    )
    list_filter = ("is_active", "subscribed_at",)
    readonly_fields = ("subscribed_at", "updated_at",)

    search_help_text = (
        "Search by subscriber email."
    )

    ordering = (
        "-subscribed_at",
    )

    list_per_page = 25
    show_full_result_count = False
    empty_value_display = "—"

admin_site.register(User, CustomUserAdmin,)
admin_site.register(NewsletterSubscriber, NewsletterSubscriberAdmin,)