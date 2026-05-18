from __future__ import annotations

import logging

from collections import defaultdict
from typing import Any

from django import template
from django.core.cache import cache

from apps.site_settings.models import SettingGroup
from vastrika_backend.admin_site import admin_site

register = template.Library()

logger = logging.getLogger(__name__)

# =========================================================
# PROFESSIONAL SIDEBAR CONFIGURATION
# =========================================================

SIDEBAR_CONFIG = {
    "products": {
        "title": "Products",
        "icon": "inventory_2",
        "order": 1,
        "models": {
            "product": {
                "icon": "shopping_bag",
                "order": 1,
            },
            "brand": {
                "icon": "store",
                "order": 2,
            },
            "producttag": {
                "icon": "local_offer",
                "order": 3,
            },
            "productimage": {
                "icon": "image",
                "order": 4,
            },
        },
    },
    "categories": {
        "title": "Product Categories",
        "icon": "category",
        "order": 2,
        "models": {
            "parentcategory": {
                "icon": "folder",
                "order": 1,
            },
            "subcategory": {
                "icon": "layers",
                "order": 2,
            },
            "childcategory": {
                "icon": "category",
                "order": 3,
            },
        },
    },
    "inventory": {
        "title": "Inventory",
        "icon": "warehouse",
        "order": 3,
        "models": {
            "stock": {
                "icon": "inventory_2",
                "order": 1,
            },
            "productvariant": {
                "icon": "tune",
                "order": 2,
            },
            "warehouse": {
                "icon": "warehouse",
                "order": 3,
            },
        },
    },
    "orders": {
        "title": "Orders",
        "icon": "receipt_long",
        "order": 4,
        "models": {
            "order": {
                "icon": "shopping_cart",
                "order": 1,
            },
            "payment": {
                "icon": "payments",
                "order": 2,
            },
            "refund": {
                "icon": "undo",
                "order": 3,
            },
            "invoice": {
                "icon": "receipt_long",
                "order": 4,
            },
        },
    },
    "customers": {
        "title": "Customers",
        "icon": "groups",
        "order": 5,
        "models": {
            "customer": {
                "icon": "person",
                "order": 1,
            },
            "cartitem": {
                "icon": "shopping_cart",
                "order": 2,
            },
            "wishlistitem": {
                "icon": "favorite",
                "order": 3,
            },
            "review": {
                "icon": "rate_review",
                "order": 4,
            },
        },
    },
    "marketing": {
        "title": "Marketing",
        "icon": "campaign",
        "order": 6,
        "models": {
            "newslettersubscriber": {
                "icon": "mail",
                "order": 1,
            },
        },
    },
    "reports": {
        "title": "Reports",
        "icon": "bar_chart",
        "order": 7,
        "models": {
            "salesreport": {
                "icon": "bar_chart",
                "order": 1,
            },
            "productreport": {
                "icon": "inventory_2",
                "order": 2,
            },
            "customerreport": {
                "icon": "groups",
                "order": 3,
            },
        },
    },
}

# =========================================================
# FALLBACK ICONS
# =========================================================

DEFAULT_MODEL_ICON = "chevron_right"
DEFAULT_SECTION = "Others"
DEFAULT_SECTION_ICON = "more_horiz"

# =========================================================
# SETTINGS MENU ORDER
# =========================================================

SETTINGS_ORDER = {
    "General Settings": 1,
    "Appearance Settings": 2,
    "Security Settings": 3,
    "Notification Settings": 4,
    "Payment Settings": 5,
    "Shipping Settings": 6,
}

# =========================================================
# UTILITIES
# =========================================================


def get_model_key(model: dict[str, Any]) -> str:
    """
    Extract clean model key from admin_url dynamically.

    Example:
    /admin/products/product/
    -> product
    """

    admin_url = model.get("admin_url", "")

    if not admin_url:
        return ""

    parts = [part for part in admin_url.split("/") if part]

    if len(parts) >= 3:
        return parts[-1].lower()

    return ""


def get_section_by_model(model_key: str) -> tuple[str, dict[str, Any]]:
    """
    Dynamically find sidebar section from model key.
    """

    for _, section_config in SIDEBAR_CONFIG.items():
        models = section_config.get("models", {})

        if model_key in models:
            return section_config["title"], section_config

    return DEFAULT_SECTION, {
        "title": DEFAULT_SECTION,
        "icon": DEFAULT_SECTION_ICON,
        "order": 999,
        "models": {},
    }


# =========================================================
# MAIN SIDEBAR GENERATOR
# =========================================================


@register.simple_tag(takes_context=True)
def get_grouped_admin_sidebar(context):
    """
    Enterprise-grade dynamic admin sidebar.
    """

    request = context["request"]

    cache_key = f"admin_sidebar_{request.user.pk}"

    cached_sidebar = cache.get(cache_key)

    if cached_sidebar:
        return cached_sidebar

    app_list = admin_site.get_app_list(request)

    grouped_data = defaultdict(list)

    for app in app_list:
        for model in app.get("models", []):

            model_key = get_model_key(model)

            section_title, section_config = get_section_by_model(model_key)

            model_config = (
                section_config.get("models", {}).get(model_key, {})
            )

            model["icon"] = model_config.get(
                "icon",
                DEFAULT_MODEL_ICON,
            )

            model["order"] = model_config.get("order", 999)

            model["model_key"] = model_key

            grouped_data[section_title].append(model)

    final_sections = []

    for _, section_config in sorted(
        SIDEBAR_CONFIG.items(),
        key=lambda item: item[1].get("order", 999),
    ):

        section_title = section_config["title"]

        items = grouped_data.get(section_title, [])

        if not items:
            continue

        items = sorted(
            items,
            key=lambda item: item.get("order", 999),
        )

        final_sections.append(
            {
                "title": section_title,
                "icon": section_config["icon"],
                "order": section_config["order"],
                "items": items,
            }
        )

    # =====================================================
    # HANDLE UNKNOWN / THIRD PARTY MODELS
    # =====================================================

    known_sections = [
        config["title"]
        for config in SIDEBAR_CONFIG.values()
    ]

    others = []

    for section_name, models in grouped_data.items():
        if section_name not in known_sections:
            others.extend(models)

    if others:
        final_sections.append(
            {
                "title": DEFAULT_SECTION,
                "icon": DEFAULT_SECTION_ICON,
                "order": 999,
                "items": sorted(
                    others,
                    key=lambda item: item.get("name", ""),
                ),
            }
        )

    # =====================================================
    # CACHE
    # =====================================================

    cache.set(cache_key, final_sections, timeout=300)

    return final_sections


# =========================================================
# SETTINGS MENU
# =========================================================


@register.simple_tag
def get_dynamic_settings_menu():
    """
    Dynamic settings sidebar menu.
    """

    cache_key = "dynamic_settings_menu"

    cached_menu = cache.get(cache_key)

    if cached_menu:
        return cached_menu

    try:
        settings_menu = (
            SettingGroup.objects.filter(is_active=True)
            .select_related("level")
            .order_by("name")
        )

        sorted_menu = sorted(
            settings_menu,
            key=lambda item: SETTINGS_ORDER.get(item.name, 999),
        )

        cache.set(cache_key, sorted_menu, timeout=300)

        return sorted_menu

    except Exception as exc:
        logger.exception(
            "Failed to generate dynamic settings menu: %s",
            exc,
        )
        return []