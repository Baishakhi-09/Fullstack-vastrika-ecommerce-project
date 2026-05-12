from django import template
from vastrika_backend.admin_site import admin_site
from apps.site_settings.models import SettingGroup

register = template.Library()

SECTION_ORDER = [
    "Products",
    "Product Categories",
    "Inventory",
    "Orders",
    "Customers",
    "Marketing",
    "Reports",
    "Others",
]

SECTION_ICONS = {
    "Products": "inventory_2",
    "Product Categories": "category",
    "Inventory": "warehouse",
    "Orders": "receipt_long",
    "Customers": "groups",
    "Marketing": "campaign",
    "Reports": "bar_chart",
    "Others": "more_horiz",
}

MODEL_ICONS = {
    # Products
    "Brands": "store",
    "Product tags": "local_offer",
    "Products": "shopping_bag",
    "Product images": "image",

    # Categories
    "Parent Categories": "folder",
    "Sub Categories": "layers",
    "Child Categories": "category",

    # Inventory
    "Product variants": "tune",         
    "Stocks": "inventory_2",   
    "Warehouses": "warehouse",

    # Order
    "Orders": "shopping_cart",
    "Payments": "payments",
    "Refunds": "undo",
    "Invoices": "receipt_long",

    # Customers
    "Customers": "person",
    "Cart items": "shopping_cart",
    "Wishlist items": "favorite",
    "Reviews": "rate_review",

    # Marketing / Other
    "Newsletter Subscribers": "mail",
    "Admin notifications": "notifications",

    # System
    "Users": "person",
    "Groups": "admin_panel_settings",

    "Sales reports": "bar_chart",
    "Product reports": "inventory_2",
    "Customer reports": "groups",

    "Setting Levels": "settings_applications",
    "Setting Groups": "settings",
    "Setting Fields": "tune",
    "Setting Files": "attach_file",
}


MODEL_ORDER = {
    "Products": {
        "Products": 1,
        "Brands": 2,
        "Product tags": 3,      
        "Product images": 4,    
    },
    "Product Categories": {
        "Parent Categories": 1,
        "Sub Categories": 2,
        "Child Categories": 3,
    },
    "Orders": {
        "Orders": 1,
        "Payments": 2,
        "Refunds": 3,
        "Invoices": 4,
    },
    "Customers": {
        "Customers": 1,
        "Cart items": 2,
        "Wishlist items": 3,
        "Reviews": 4,
    },

    "Reports": {
        "Sales reports": 1,
        "Product reports": 2,
        "Customer reports": 3,
    },
}

SETTINGS_ORDER = {
        "General Settings": 1,
        "Appearance Settings": 2,
        "Security Settings": 3,
        "Notification Settings": 4,
        "Payment Settings": 5,
        "Shipping Settings": 6,
    }

def get_section_from_url(admin_url: str) -> str:
    admin_url = admin_url.lower()

    if "/products/product/" in admin_url:
        return "Products"
    if "/products/brand/" in admin_url:
        return "Products"
    if "/products/productimage/" in admin_url:
        return "Products"
    if "/products/producttag/" in admin_url:
        return "Products"
    
    if "/products/parentcategory/" in admin_url:
        return "Product Categories"
    if "/products/subcategory/" in admin_url:
        return "Product Categories"
    if "/products/childcategory/" in admin_url:
        return "Product Categories"
    
    if "/products/stock/" in admin_url:
        return "Inventory"    
    if "/products/productvariant/" in admin_url:
        return "Inventory"
    if "/products/warehouse/" in admin_url:
        return "Inventory"
    
    if "/orders/order/" in admin_url:
        return "Orders"
    if "/orders/payment/" in admin_url:
        return "Orders"
    if "/orders/refund/" in admin_url:
        return "Orders"
    if "/orders/invoice/" in admin_url:
        return "Orders"
    
    if "/customers/customer/" in admin_url:
        return "Customers"
    if "/customers/review/" in admin_url:
        return "Customers"
    if "/products/cartitem/" in admin_url:
        return "Customers"
    if "/products/wishlistitem/" in admin_url:
        return "Customers"
    
    if "/reports/salesreport/" in admin_url:
        return "Reports"
    if "/reports/productreport/" in admin_url:
        return "Reports"
    if "/reports/customerreport/" in admin_url:
        return "Reports"
    
    if "/accounts/newslettersubscriber/" in admin_url:
        return "Marketing"
    
    # if "/accounts/user/" in admin_url:
    #     return "Others"
    # if "/auth/group/" in admin_url:
    #     return "Others"
    # if "/products/adminnotification/" in admin_url:
    #     return "Others"
    
    # return None

    return "Others"


@register.simple_tag(takes_context=True)
def get_grouped_admin_sidebar(context):
    request = context["request"]
    app_list = admin_site.get_app_list(request)

    grouped = {section: [] for section in SECTION_ORDER}
    # others = []

    for app in app_list:
        for model in app.get("models", []):
            admin_url = model.get("admin_url", "")
            model_name = model.get("name", "")
            section = get_section_from_url(admin_url)

            model["icon"] = MODEL_ICONS.get(model_name, "chevron_right")

            grouped.setdefault(section, []).append(model)

            # if section:
            #     grouped[section].append(model)
            # else:
            #     others.append(model)

    final_sections = []

    for section in SECTION_ORDER:
        items = grouped.get(section, [])

        if items:

            items = sorted(
                items,
                key=lambda x: MODEL_ORDER.get(section, {}).get(x.get("name"), 99),
            )

            final_sections.append({
                "title": section,
                "icon": SECTION_ICONS.get(section, "folder"),
                "items": items,
            })

    # if others:
    #     final_sections.append({
    #          "title": "Others",
    #         "icon": "folder_open",
    #         "items": others,
    #     })

    return final_sections

@register.simple_tag
def get_dynamic_settings_menu():
    try:
        settings_menu = SettingGroup.objects.filter(
            is_active=True
        ).select_related("level")

        return sorted(
            settings_menu,
            key=lambda item: SETTINGS_ORDER.get(item.name, 99)
        )
    except Exception:
        return []