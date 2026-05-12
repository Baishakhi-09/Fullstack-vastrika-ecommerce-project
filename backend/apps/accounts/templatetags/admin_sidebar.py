from functools import lru_cache
from typing import Dict, Any, List
import logging

from django import template

from vastrika_backend.admin_site import admin_site
from apps.site_settings.models import SettingGroup

from apps.accounts.constants import (
    SECTION_OTHERS,
)

from apps.accounts.sidebar_config import (
    SECTION_ORDER,
    SECTION_ICONS,
    SIDEBAR_CONFIG,
    SETTINGS_ORDER,
)

register = template.Library()

logger = logging.getLogger(__name__)


# HELPERS
@lru_cache(maxsize=256)
def get_model_config(
    app_label: str,
    model_name: str,
) -> Dict[str, Any]:
    """
    Cached sidebar model configuration lookup.
    """

    return SIDEBAR_CONFIG.get(
        (app_label.lower(), model_name.lower()),
        {
            "section": SECTION_OTHERS,
            "icon": "chevron_right",
            "order": 99,
        },
    )

# ADMIN SIDEBAR
@register.simple_tag(takes_context=True)
def get_grouped_admin_sidebar(
    context: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Dynamically build grouped admin sidebar.
    """

    request = context.get("request")

    if request is None:
        return []

    try:
        app_list = admin_site.get_app_list(request)

        grouped = {
            section: []
            for section in SECTION_ORDER
        }

        for app in app_list:
            app_label = app.get(
                "app_label",
                "",
            ).lower()

            for model in app.get("models", []):
                model_object_name = model.get(
                    "object_name",
                    "",
                ).lower()

                config = get_model_config(
                    app_label,
                    model_object_name,
                )

                model["icon"] = config["icon"]
                model["menu_order"] = config["order"]

                grouped.setdefault(
                    config["section"],
                    [],
                ).append(model)

        final_sections = []

        for section in SECTION_ORDER:
            items = grouped.get(section, [])

            if not items:
                continue

            sorted_items = sorted(
                items,
                key=lambda item: item.get(
                    "menu_order",
                    99,
                ),
            )

            final_sections.append({
                "title": section,
                "icon": SECTION_ICONS.get(
                    section,
                    "folder",
                ),
                "items": sorted_items,
            })

        return final_sections
            
    except Exception:
        logger.exception(
            "Failed to generate admin sidebar.",
        )

        return []
    
# DYNAMIC SETTINGS MENU
@register.simple_tag
def get_dynamic_settings_menu() -> List[SettingGroup]:
    """
    Load active settings groups dynamically.
    """

    try:
        settings_menu = (
            SettingGroup.objects
            .filter(is_active=True)
            .select_related("level")
            .order_by("name")
        )

        return sorted(
            settings_menu,
            key=lambda item: SETTINGS_ORDER.get(
                item.name,
                99,
            ),
        )
    
    except Exception:
        logger.exception(
            "Failed to load dynamic settings menu.",
        )

        return []