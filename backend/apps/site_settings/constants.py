# -------------------- FIELD TYPES -------------------- #
from enum import Enum

class FieldType(str, Enum):
    TEXT = "text"
    FILE = "file"
    SELECT = "select"


# -------------------- COMMON OPTIONS -------------------- #
TIMEZONE_OPTIONS = [
    {"label": "Asia/Kolkata", "value": "Asia/Kolkata"},
    {"label": "UTC", "value": "UTC"},
]

LANGUAGE_OPTIONS = [
    {"label": "English", "value": "en"},
    {"label": "Bengali", "value": "bn"},
    {"label": "Hindi", "value": "hi"},
]

CURRENCY_OPTIONS = [
    {"label": "INR - Indian Rupee", "value": "INR"},
    {"label": "USD - US Dollar", "value": "USD"},
]

DATE_FORMAT_OPTIONS = [
    {"label": "DD/MM/YYYY", "value": "DD/MM/YYYY"},
    {"label": "MM/DD/YYYY", "value": "MM/DD/YYYY"},
    {"label": "YYYY-MM-DD", "value": "YYYY-MM-DD"},
]

TIME_FORMAT_OPTIONS = [
    {"label": "12 Hour", "value": "12"},
    {"label": "24 Hour", "value": "24"},
]


# -------------------- GENERAL SETTINGS -------------------- #
GENERAL_SETTINGS_FIELDS = [
    {
        "label": "Site Name",
        "key": "site_name",
        "field_type": FieldType.TEXT,
        "default_value": "Vastrika",
        "placeholder": "Enter site name",
        "required": True,
    },
    {
        "label": "Site Logo",
        "key": "site_logo",
        "field_type": FieldType.FILE,
        "default_value": None,
    },
    {
        "label": "Site Favicon",
        "key": "site_favicon",
        "field_type": FieldType.FILE,
        "default_value": None,
    },
    {
        "label": "Timezone",
        "key": "timezone",
        "field_type": FieldType.SELECT,
        "default_value": "Asia/Kolkata",
        "options": TIMEZONE_OPTIONS,
    },
    {
        "label": "Language",
        "key": "language",
        "field_type": FieldType.SELECT,
        "default_value": "en",
        "options": LANGUAGE_OPTIONS,
    },
    {
        "label": "Currency",
        "key": "currency",
        "field_type": FieldType.SELECT,
        "default_value": "INR",
        "options": CURRENCY_OPTIONS,
    },
    {
        "label": "Date Format",
        "key": "date_format",
        "field_type": FieldType.SELECT,
        "default_value": "DD/MM/YYYY",
        "options": DATE_FORMAT_OPTIONS,
    },
    {
        "label": "Time Format",
        "key": "time_format",
        "field_type": FieldType.SELECT,
        "default_value": "12",
        "options": TIME_FORMAT_OPTIONS,
    },
]