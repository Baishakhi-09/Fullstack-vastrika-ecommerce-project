from __future__ import annotations

from typing import Any

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from vastrika_backend.admin_site import admin_site

from .models import NewsletterSubscriber, User


# USER ADMIN
@admin.register(User, site=admin_site)
class CustomUserAdmin(UserAdmin):
    """
    Enterprise-grade custom user admin.
    """

    # CONFIG
    ordering = ("-id",)

    list_per_page = 25

    empty_value_display = "-"

    save_on_top = True

    show_full_result_count = True

    date_hierarchy = "date_joined"

    # LIST VIEW
    list_display = (
        "id",
        "profile_preview",
        "username",
        "email",
        "phone",
        "role_badge",
        "status_badge",
        "is_staff",
        "is_superuser",
        "last_login",
        "date_joined",
    )

    list_display_links = (
        "id",
        "username",
    )

    list_filter = (
        "role",
        "gender",
        "is_staff",
        "is_superuser",
        "is_active",
        ("date_joined", admin.DateFieldListFilter),
        ("last_login", admin.DateFieldListFilter),
    )

    search_fields = (
        "^username",
        "^email",
        "^phone",
    )

    readonly_fields = (
        "profile_preview",
        "last_login",
        "date_joined",
    )

    # FIELDSETS
    fieldsets = (
        (
            "Authentication",
            {
                "fields": (
                    "username",
                    "password",
                ),
            },
        ),
        (
            "Personal Information",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "phone",
                    "alternate_phone",
                    "gender",
                    "role",
                ),
            },
        ),
        (
            "Profile Information",
            {
                "fields": (
                    "profile_preview",
                    "profile_image",
                ),
            },
        ),
        (
            "Address Information",
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
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            "Important Dates",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                ),
            },
        ),
    )

    # ADD USER
    add_fieldsets = (
        (
            "Create User",
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "phone",
                    "role",
                    "profile_image",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    # CUSTOM DISPLAY METHODS
    @admin.display(
        description="Profile",
        ordering="username",
    )
    def profile_preview(self, obj: User) -> str:

        if obj and obj.profile_image:

            return format_html(
                """
                <img
                    src="{}"
                    class="admin-profile-preview"
                    alt="Profile"/>
                """,
                obj.profile_image.url,
            )

        return format_html(
            """
            <div class="admin-profile-placeholder">
                N/A
            </div>
            """
        )

    @admin.display(
        description="Role",
        ordering="role",
    )
    def role_badge(self, obj: User) -> str:

        role = obj.role.title() if obj.role else "User"

        return format_html(
            """
            <span class="admin-badge admin-role-badge">
                {}
            </span>
            """,
            role,
        )

    @admin.display(
        description="Status",
        ordering="is_active",
    )

    def status_badge(self, obj: User) -> str:

        css_class = (
            "admin-status-active"
            if obj.is_active
            else "admin-status-inactive"
        )

        label = (
            "Active"
            if obj.is_active
            else "Inactive"
        )

        return format_html(
            """
            <span class="admin-badge {}">
                {}
            </span>
            """,
            css_class,
            label,
        )


# NEWSLETTER SUBSCRIBER ADMIN
@admin.register(NewsletterSubscriber, site=admin_site)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    """
    Enterprise-grade newsletter subscriber admin.
    """

    # CONFIG
    ordering = ("-subscribed_at",)

    list_per_page = 25

    empty_value_display = "-"

    save_on_top = True

    show_full_result_count = True

    date_hierarchy = "subscribed_at"

    # LIST VIEW
    list_display = (
        "id",
        "email",
        "status_badge",
        "subscribed_at",
        "updated_at",
    )

    list_display_links = (
        "id",
        "email",
    )

    list_filter = (
        "is_active",
        ("subscribed_at", admin.DateFieldListFilter),
        ("updated_at", admin.DateFieldListFilter),
    )

    search_fields = (
        "^email",
    )

    readonly_fields = (
        "subscribed_at",
        "updated_at",
    )

    # FIELDSETS
    fieldsets = (
        (
            "Subscriber Information",
            {
                "fields": (
                    "email",
                    "is_active",
                ),
            },
        ),
        (
            "System Information",
            {
                "fields": (
                    "subscribed_at",
                    "updated_at",
                ),
            },
        ),
    )

    # ACTIONS
    actions = (
        "activate_subscribers",
        "deactivate_subscribers",
    )

    @admin.action(description="Activate selected subscribers")
    def activate_subscribers(
        self,
        request: Any,
        queryset,
    ) -> None:

        updated_count = queryset.update(is_active=True)

        self.message_user(
            request,
            f"{updated_count} subscribers activated successfully.",
        )

    @admin.action(description="Deactivate selected subscribers")
    def deactivate_subscribers(
        self,
        request: Any,
        queryset,
    ) -> None:

        updated_count = queryset.update(is_active=False)

        self.message_user(
            request,
            f"{updated_count} subscribers deactivated successfully.",
        )

    #  CUSTOM DISPLAY METHODS
    @admin.display(
        description="Status",
        ordering="is_active",
    )
    def status_badge(
        self,
        obj: NewsletterSubscriber,
    ) -> str:

        css_class = (
            "admin-status-active"
            if obj.is_active
            else "admin-status-inactive"
        )

        label = (
            "Active"
            if obj.is_active
            else "Inactive"
        )

        return format_html(
            """
            <span class="admin-badge {}">
                {}
            </span>
            """,
            css_class,
            label,
        )