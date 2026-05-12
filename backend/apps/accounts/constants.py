from django.db.models import TextChoices

# User Roles
class UserRole(TextChoices):
    ADMIN = "admin", "Admin"
    MANAGER = "manager", "Manager"
    EDITOR = "editor", "Editor"
    USER = "user", "User"

# Dashboard Sections
SECTION_PRODUCTS = "Products"
SECTION_PRODUCT_CATEGORIES = "Product Categories"
SECTION_INVENTORY = "Inventory"
SECTION_ORDERS = "Orders"
SECTION_CUSTOMERS = "Customers"
SECTION_MARKETING = "Marketing"
SECTION_REPORTS = "Reports"
SECTION_OTHERS = "Others"