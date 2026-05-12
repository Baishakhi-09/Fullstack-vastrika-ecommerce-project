from typing import Dict, Tuple, Any, List

from apps.accounts.constants import (
    SECTION_PRODUCTS,
    SECTION_PRODUCT_CATEGORIES,
    SECTION_INVENTORY,
    SECTION_ORDERS,
    SECTION_CUSTOMERS,
    SECTION_MARKETING,
    SECTION_REPORTS,
    SECTION_OTHERS,
)

# =========================================================
# SECTION ORDER
# =========================================================

SECTION_ORDER: List[str] = [
    SECTION_PRODUCTS,
    SECTION_PRODUCT_CATEGORIES,
    SECTION_INVENTORY,
    SECTION_ORDERS,
    SECTION_CUSTOMERS,
    SECTION_MARKETING,
    SECTION_REPORTS,
    SECTION_OTHERS,
]

# =========================================================
# SECTION ICONS
# =========================================================

SECTION_ICONS: Dict[str, str] = {
    SECTION_PRODUCTS: "inventory_2",
    SECTION_PRODUCT_CATEGORIES: "category",
    SECTION_INVENTORY: "warehouse",
    SECTION_ORDERS: "receipt_long",
    SECTION_CUSTOMERS: "groups",
    SECTION_MARKETING: "campaign",
    SECTION_REPORTS: "bar_chart",
    SECTION_OTHERS: "more_horiz",
}

# =========================================================
# SIDEBAR CONFIG
# =========================================================

SIDEBAR_CONFIG: Dict[
    Tuple[str, str],
    Dict[str, Any],
] = {

    # =====================================================
    # PRODUCTS
    # =====================================================

    ("products", "product"): {
        "section": SECTION_PRODUCTS,
        "icon": "shopping_bag",
        "order": 1,
    },

    ("products", "brand"): {
        "section": SECTION_PRODUCTS,
        "icon": "store",
        "order": 2,
    },

    ("products", "producttag"): {
        "section": SECTION_PRODUCTS,
        "icon": "local_offer",
        "order": 3,
    },

    ("products", "productimage"): {
        "section": SECTION_PRODUCTS,
        "icon": "image",
        "order": 4,
    },

    # =====================================================
    # PRODUCT CATEGORIES
    # =====================================================

    ("products", "parentcategory"): {
        "section": SECTION_PRODUCT_CATEGORIES,
        "icon": "folder",
        "order": 1,
    },

    ("products", "subcategory"): {
        "section": SECTION_PRODUCT_CATEGORIES,
        "icon": "layers",
        "order": 2,
    },

    ("products", "childcategory"): {
        "section": SECTION_PRODUCT_CATEGORIES,
        "icon": "category",
        "order": 3,
    },

    # =====================================================
    # INVENTORY
    # =====================================================

    ("products", "productvariant"): {
        "section": SECTION_INVENTORY,
        "icon": "tune",
        "order": 1,
    },

    ("products", "stock"): {
        "section": SECTION_INVENTORY,
        "icon": "inventory_2",
        "order": 2,
    },

    ("products", "warehouse"): {
        "section": SECTION_INVENTORY,
        "icon": "warehouse",
        "order": 3,
    },

    # =====================================================
    # ORDERS
    # =====================================================

    ("orders", "order"): {
        "section": SECTION_ORDERS,
        "icon": "shopping_cart",
        "order": 1,
    },

    ("orders", "payment"): {
        "section": SECTION_ORDERS,
        "icon": "payments",
        "order": 2,
    },

    ("orders", "refund"): {
        "section": SECTION_ORDERS,
        "icon": "undo",
        "order": 3,
    },

    ("orders", "invoice"): {
        "section": SECTION_ORDERS,
        "icon": "receipt_long",
        "order": 4,
    },

    # =====================================================
    # CUSTOMERS
    # =====================================================

    ("customers", "customer"): {
        "section": SECTION_CUSTOMERS,
        "icon": "person",
        "order": 1,
    },

    ("products", "cartitem"): {
        "section": SECTION_CUSTOMERS,
        "icon": "shopping_cart",
        "order": 2,
    },

    ("products", "wishlistitem"): {
        "section": SECTION_CUSTOMERS,
        "icon": "favorite",
        "order": 3,
    },

    ("customers", "review"): {
        "section": SECTION_CUSTOMERS,
        "icon": "rate_review",
        "order": 4,
    },

    # =====================================================
    # MARKETING
    # =====================================================

    ("accounts", "newslettersubscriber"): {
        "section": SECTION_MARKETING,
        "icon": "mail",
        "order": 1,
    },

    # =====================================================
    # REPORTS
    # =====================================================

    ("reports", "salesreport"): {
        "section": SECTION_REPORTS,
        "icon": "bar_chart",
        "order": 1,
    },

    ("reports", "productreport"): {
        "section": SECTION_REPORTS,
        "icon": "inventory_2",
        "order": 2,
    },

    ("reports", "customerreport"): {
        "section": SECTION_REPORTS,
        "icon": "groups",
        "order": 3,
    },

    # =====================================================
    # OTHERS
    # =====================================================

    ("auth", "user"): {
        "section": SECTION_OTHERS,
        "icon": "person",
        "order": 1,
    },

    ("auth", "group"): {
        "section": SECTION_OTHERS,
        "icon": "admin_panel_settings",
        "order": 2,
    },

    ("products", "adminnotification"): {
        "section": SECTION_OTHERS,
        "icon": "notifications",
        "order": 3,
    },

    # =====================================================
    # SETTINGS
    # =====================================================

    ("site_settings", "settinglevel"): {
        "section": SECTION_OTHERS,
        "icon": "settings_applications",
        "order": 4,
    },

    ("site_settings", "settinggroup"): {
        "section": SECTION_OTHERS,
        "icon": "settings",
        "order": 5,
    },

    ("site_settings", "settingfield"): {
        "section": SECTION_OTHERS,
        "icon": "tune",
        "order": 6,
    },

    ("site_settings", "settingfile"): {
        "section": SECTION_OTHERS,
        "icon": "attach_file",
        "order": 7,
    },
}

# =========================================================
# SETTINGS ORDER
# =========================================================

SETTINGS_ORDER: Dict[str, int] = {
    "General Settings": 1,
    "Appearance Settings": 2,
    "Security Settings": 3,
    "Notification Settings": 4,
    "Payment Settings": 5,
    "Shipping Settings": 6,
}