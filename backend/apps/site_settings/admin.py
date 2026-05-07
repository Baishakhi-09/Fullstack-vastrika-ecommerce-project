from django.contrib import admin
from vastrika_backend.admin_site import admin_site

from .models import SettingLevel, SettingGroup, SettingField, SettingFile


# -------------------- SETTING GROUP INLINE -------------------- #
class SettingGroupInline(admin.TabularInline):
    model = SettingGroup
    extra = 0
    fields = (
        "name",
        "key",
        "icon",
        "description",
        "order",
        "is_active",
    )
    readonly_fields = ()
    ordering = ("order",)


# -------------------- SETTING FIELD INLINE -------------------- #
class SettingFieldInline(admin.TabularInline):
    model = SettingField
    extra = 0
    fields = (
        "label",
        "key",
        "field_type",
        "placeholder",
        "help_text",
        "default_value",
        "value",
        "options",
        "is_required",
        "is_active",
        "order",
    )
    ordering = ("order",)


# -------------------- SETTING LEVEL ADMIN -------------------- #
@admin.register(SettingLevel, site=admin_site)
class SettingLevelAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "key",
        "order",
        "is_active",
    )
    list_editable = (
        "order",
        "is_active",
    )
    search_fields = (
        "name",
        "key",
    )
    prepopulated_fields = {
        "key": ("name",),
    }
    ordering = ("order", "name")
    inlines = [SettingGroupInline]


# -------------------- SETTING GROUP ADMIN -------------------- #
@admin.register(SettingGroup, site=admin_site)
class SettingGroupAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "level",
        "key",
        "icon",
        "order",
        "is_active",
    )
    list_editable = (
        "order",
        "is_active",
    )
    search_fields = (
        "name",
        "key",
        "description",
        "level__name",
    )
    list_filter = (
        "level",
        "is_active",
    )
    prepopulated_fields = {
        "key": ("name",),
    }
    ordering = (
        "level__order",
        "order",
        "name",
    )
    inlines = [SettingFieldInline]


# -------------------- SETTING FIELD ADMIN -------------------- #
@admin.register(SettingField, site=admin_site)
class SettingFieldAdmin(admin.ModelAdmin):
    list_display = (
        "label",
        "key",
        "group",
        "field_type",
        "is_required",
        "is_active",
        "order",
    )
    list_editable = (
        "is_required",
        "is_active",
        "order",
    )
    search_fields = (
        "label",
        "key",
        "group__name",
        "group__level__name",
    )
    list_filter = (
        "group__level",
        "group",
        "field_type",
        "is_required",
        "is_active",
    )
    readonly_fields = (
        "current_value",
    )
    prepopulated_fields = {
        "key": ("label",),
    }
    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "group",
                    "label",
                    "key",
                    "field_type",
                )
            },
        ),
        (
            "Field Content",
            {
                "fields": (
                    "placeholder",
                    "help_text",
                    "default_value",
                    "value",
                    "options",
                    "current_value",
                )
            },
        ),
        (
            "Validation & Visibility",
            {
                "fields": (
                    "is_required",
                    "is_active",
                    "order",
                )
            },
        ),
    )
    ordering = (
        "group__level__order",
        "group__order",
        "order",
        "label",
    )

    @admin.display(description="Current Value")
    def current_value(self, obj):
        return obj.get_value()


# -------------------- SETTING FILE ADMIN -------------------- #
@admin.register(SettingFile, site=admin_site)
class SettingFileAdmin(admin.ModelAdmin):
    list_display = (
        "field",
        "file",
        "uploaded_at",
    )
    search_fields = (
        "field__label",
        "field__key",
    )
    list_filter = (
        "uploaded_at",
    )
    readonly_fields = (
        "uploaded_at",
    )
    ordering = ("-uploaded_at",)