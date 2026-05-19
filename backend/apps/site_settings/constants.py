from __future__ import annotations

from django.db import models
from django.utils.translation import (
    gettext_lazy as _,
)

# =========================================================
# FIELD TYPES
# =========================================================
class FieldType(models.TextChoices):

    TEXT = (
        "text",
        _("Text"),
    )

    TEXTAREA = (
        "textarea",
        _("Textarea"),
    )

    RICH_TEXT = (
        "rich_text",
        _("Rich Text"),
    )

    NUMBER = (
        "number",
        _("Number"),
    )

    BOOLEAN = (
        "boolean",
        _("Boolean"),
    )

    EMAIL = (
        "email",
        _("Email"),
    )

    URL = (
        "url",
        _("URL"),
    )

    FILE = (
        "file",
        _("File"),
    )

    IMAGE = (
        "image",
        _("Image"),
    )

    SELECT = (
        "select",
        _("Select"),
    )

    MULTISELECT = (
        "multiselect",
        _("Multi Select"),
    )

    COLOR = (
        "color",
        _("Color"),
    )

    JSON = (
        "json",
        _("JSON"),
    )


# =========================================================
# COMMON OPTIONS
# =========================================================
TIMEZONE_OPTIONS = (

    {
        "label": "Asia/Kolkata",
        "value": "Asia/Kolkata",
    },

    {
        "label": "UTC",
        "value": "UTC",
    },

    {
        "label": "America/New_York",
        "value": "America/New_York",
    },
)

LANGUAGE_OPTIONS = (

    {
        "label": "English",
        "value": "en",
    },

    {
        "label": "Bengali",
        "value": "bn",
    },

    {
        "label": "Hindi",
        "value": "hi",
    },
)

CURRENCY_OPTIONS = (

    {
        "label": "INR - Indian Rupee",
        "value": "INR",
    },

    {
        "label": "USD - US Dollar",
        "value": "USD",
    },

    {
        "label": "EUR - Euro",
        "value": "EUR",
    },
)

DATE_FORMAT_OPTIONS = (

    {
        "label": "DD/MM/YYYY",
        "value": "DD/MM/YYYY",
    },

    {
        "label": "MM/DD/YYYY",
        "value": "MM/DD/YYYY",
    },

    {
        "label": "YYYY-MM-DD",
        "value": "YYYY-MM-DD",
    },
)

TIME_FORMAT_OPTIONS = (

    {
        "label": "12 Hour",
        "value": "12",
    },

    {
        "label": "24 Hour",
        "value": "24",
    },
)

BOOLEAN_OPTIONS = (

    {
        "label": "Yes",
        "value": True,
    },

    {
        "label": "No",
        "value": False,
    },
)


# =========================================================
# GENERAL SETTINGS FIELDS
# =========================================================
GENERAL_SETTINGS_FIELDS = (

    {
        "label": _("Site Name"),
        "key": "site_name",
        "field_type": FieldType.TEXT,
        "default_value": "Vastrika",
        "placeholder": _("Enter site name"),
        "help_text": _(
            "Main website name."
        ),
        "is_required": True,
        "order": 1,
    },

    {
        "label": _("Site Logo"),
        "key": "site_logo",
        "field_type": FieldType.IMAGE,
        "default_value": None,
        "help_text": _(
            "Upload main website logo."
        ),
        "is_required": False,
        "order": 2,
    },

    {
        "label": _("Site Favicon"),
        "key": "site_favicon",
        "field_type": FieldType.IMAGE,
        "default_value": None,
        "help_text": _(
            "Upload browser favicon."
        ),
        "is_required": False,
        "order": 3,
    },

    {
        "label": _("Timezone"),
        "key": "timezone",
        "field_type": FieldType.SELECT,
        "default_value": "Asia/Kolkata",
        "options": TIMEZONE_OPTIONS,
        "help_text": _(
            "Default application timezone."
        ),
        "is_required": True,
        "order": 4,
    },

    {
        "label": _("Language"),
        "key": "language",
        "field_type": FieldType.SELECT,
        "default_value": "en",
        "options": LANGUAGE_OPTIONS,
        "help_text": _(
            "Default application language."
        ),
        "is_required": True,
        "order": 5,
    },

    {
        "label": _("Currency"),
        "key": "currency",
        "field_type": FieldType.SELECT,
        "default_value": "INR",
        "options": CURRENCY_OPTIONS,
        "help_text": _(
            "Default ecommerce currency."
        ),
        "is_required": True,
        "order": 6,
    },

    {
        "label": _("Date Format"),
        "key": "date_format",
        "field_type": FieldType.SELECT,
        "default_value": "DD/MM/YYYY",
        "options": DATE_FORMAT_OPTIONS,
        "help_text": _(
            "Global date format."
        ),
        "is_required": True,
        "order": 7,
    },

    {
        "label": _("Time Format"),
        "key": "time_format",
        "field_type": FieldType.SELECT,
        "default_value": "12",
        "options": TIME_FORMAT_OPTIONS,
        "help_text": _(
            "Global time format."
        ),
        "is_required": True,
        "order": 8,
    },

    {
        "label": _("Maintenance Mode"),
        "key": "maintenance_mode",
        "field_type": FieldType.BOOLEAN,
        "default_value": False,
        "options": BOOLEAN_OPTIONS,
        "help_text": _(
            "Enable maintenance mode."
        ),
        "is_required": True,
        "order": 9,
    },

    {
        "label": _("Support Email"),
        "key": "support_email",
        "field_type": FieldType.EMAIL,
        "default_value": "",
        "placeholder": _(
            "support@example.com"
        ),
        "help_text": _(
            "Customer support email address."
        ),
        "is_required": False,
        "order": 10,
    },

    {
        "label": _("Primary Theme Color"),
        "key": "primary_theme_color",
        "field_type": FieldType.COLOR,
        "default_value": "#000000",
        "help_text": _(
            "Main application theme color."
        ),
        "is_required": False,
        "order": 11,
    },
)