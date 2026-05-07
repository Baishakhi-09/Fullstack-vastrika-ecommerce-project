from .constants import GENERAL_SETTINGS_FIELDS
from .models import SettingLevel, SettingGroup, SettingField


def create_default_settings():
    core, _ = SettingLevel.objects.update_or_create(
        key="core",
        defaults={
            "name": "Core",
            "order": 1,
            "is_active": True,
        },
    )

    group, _ = SettingGroup.objects.update_or_create(
        key="general-settings",
        defaults={
            "level": core,
            "name": "General Settings",
            "icon": "fa-solid fa-gear",
            "description": "Basic store information and configuration.",
            "order": 1,
            "is_active": True,
        },
    )

    for index, field in enumerate(GENERAL_SETTINGS_FIELDS, start=1):
        SettingField.objects.update_or_create(
            group=group,
            key=field["key"],
            defaults={
                "label": field["label"],
                "field_type": field["field_type"].value,
                "placeholder": field.get("placeholder", ""),
                "help_text": field.get("help_text", ""),
                "default_value": "" if field.get("default_value") is None else field.get("default_value"),
                "options": field.get("options"),
                "is_required": field.get("required", False),
                "is_active": True,
                "order": index,
            },
        )