from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.db.models import Count

from vastrika_backend.admin_site import admin_site

from .models import ( Brand, ParentCategory, SubCategory, ChildCategory, Product, ProductImage, ProductTag, ProductVariant, CartItem, WishlistItem, Stock, Warehouse,)

from .notifications.models import AdminNotification, AdminNotificationRead

# Register your models here.

# -------------------- ROLE-BASED ADMIN -------------------- #
class RoleBasedAdminMixin:
    def has_module_permission(self, request):
        return request.user.is_authenticated and (
            request.user.is_superuser
            or getattr(request.user, "role", None) == "admin"
        )

    def has_view_permission(self, request, obj=None):
        return request.user.is_authenticated

    def has_change_permission(self, request, obj=None):
        return request.user.is_authenticated and (
            request.user.is_superuser
            or getattr(request.user, "role", None) == "admin"
        )

    def has_delete_permission(self, request, obj=None):
        return request.user.is_authenticated and (
            request.user.is_superuser
            or getattr(request.user, "role", None) == "admin"
        )

    def has_add_permission(self, request):
        return request.user.is_authenticated and (
            request.user.is_superuser
            or getattr(request.user, "role", None) == "admin"
        )

# -------------------- PRODUCT ADMIN FORM -------------------- #
class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["sub_category"].queryset = SubCategory.objects.none()
        self.fields["child_category"].queryset = ChildCategory.objects.none()

        if self.instance and self.instance.pk:
            if self.instance.parent_category:
                self.fields["sub_category"].queryset = SubCategory.objects.filter(
                    parent_category=self.instance.parent_category,
                    is_active=True,
                )

            if self.instance.sub_category:
                self.fields["child_category"].queryset = ChildCategory.objects.filter(
                    sub_category=self.instance.sub_category,
                    is_active=True,
                )

        if "parent_category" in self.data:
            try:
                parent_id = int(self.data.get("parent_category"))
                self.fields["sub_category"].queryset = SubCategory.objects.filter(
                    parent_category_id=parent_id,
                    is_active=True,
                )
            except (TypeError, ValueError):
                pass

        if "sub_category" in self.data:
            try:
                sub_id = int(self.data.get("sub_category"))
                self.fields["child_category"].queryset = ChildCategory.objects.filter(
                    sub_category_id=sub_id,
                    is_active=True,
                )
            except (TypeError, ValueError):
                pass

# -------------------- INLINES -------------------- #
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image_preview", "image", "alt_text", "is_primary", "sort_order")
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="height:60px; width:60px; object-fit:cover; border-radius:6px;" />',
                obj.image.url,
            )
        return "No Image"
    
    image_preview.short_description = "Preview"

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = (
        "color",
        "size",
        "variant_sku",
        "stock",
        "reserved_stock",
        "available_stock_display",
        "is_active",
    )
    readonly_fields = ("available_stock_display",)

    def available_stock_display(self, obj):
        if obj and obj.pk:
            return obj.available_stock
        return 0
    
    available_stock_display.short_description = "Available Stock"

# -------------------- CATEGORY ADMIN -------------------- #
class ParentCategoryAdmin(RoleBasedAdminMixin, admin.ModelAdmin):
    list_display = ("name", "is_active", "sort_order", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name",)
    ordering = ("sort_order", "name")
    prepopulated_fields = {"slug": ("name",)}

class SubCategoryAdmin(RoleBasedAdminMixin, admin.ModelAdmin):
    list_display = ("name", "parent_category", "is_active", "sort_order", "created_at")
    list_filter = ("is_active", "parent_category", "created_at")
    search_fields = ("name", "parent_category__name")
    ordering = ("parent_category__name", "sort_order", "name")
    prepopulated_fields = {"slug": ("name",)}

class ChildCategoryAdmin(RoleBasedAdminMixin, admin.ModelAdmin):
    list_display = ("name", "sub_category", "get_parent_category", "is_active", "sort_order", "created_at")
    list_filter = ("is_active", "sub_category", "sub_category__parent_category", "created_at")
    search_fields = ("name", "sub_category__name", "sub_category__parent_category__name")
    ordering = ("sub_category__parent_category__name", "sub_category__name", "sort_order", "name")
    prepopulated_fields = {"slug": ("name",)}

    def get_parent_category(self, obj):
        return obj.sub_category.parent_category.name
    get_parent_category.short_description = "Parent Category"

# -------------------- BRAND ADMIN -------------------- #
class BrandAdmin(RoleBasedAdminMixin, admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)

# -------------------- TAG ADMIN -------------------- #
class ProductTagAdmin(RoleBasedAdminMixin, admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)

# -------------------- PRODUCT ADMIN -------------------- #
class ProductAdmin(RoleBasedAdminMixin, admin.ModelAdmin):
    form = ProductAdminForm

    list_display = (
        "name",
        "brand",
        "parent_category",
        "sub_category",
        "child_category",
        "gender",
        "selling_price",
        "mrp",
        "discount_display",
        "total_stock_display",
        "in_stock_display",
        "is_active",
        "is_featured",
        "is_new_arrival",
        "created_at",
    )
    list_filter = (
        "is_active",
        "is_featured",
        "is_new_arrival",
        "is_best_seller",
        "is_returnable",
        "is_exchangeable",
        "is_cod_available",
        "gender",
        "occasion",
        "brand",
        "parent_category",
        "sub_category",
        "child_category",
        "created_at",
    )
    search_fields = (
        "name",
        "slug",
        "sku",
        "short_description",
        "description",
        "brand__name",
        "parent_category__name",
        "sub_category__name",
        "child_category__name",
    )
    readonly_fields = (
        "slug",
        "sku",
        "discount_display",
        "total_stock_display",
        "in_stock_display",
        "created_at",
        "updated_at",
    )
    filter_horizontal = ("tags",)
    inlines = [ProductImageInline, ProductVariantInline]
    ordering = ("-created_at",)

    fieldsets = (
        ("Basic Information", {
            "fields": ("name", "slug", "sku", "brand", "tags")
        }),
        ("Product Categories", {
            "fields": ("parent_category", "sub_category", "child_category")
        }),
        ("Descriptions", {
            "fields": ("short_description", "description")
        }),
        ("Product Attributes", {
            "fields": ("gender", "occasion")
        }),
        ("Pricing & Ratings", {
            "fields": (
                "mrp",
                "selling_price",
                "discount_display",
                "average_rating",
                "review_count",
            )
        }),
        ("Availability", {
            "fields": (
                "total_stock_display",
                "in_stock_display",
                "is_active",
                "is_featured",
                "is_new_arrival",
                "is_best_seller",
            )
        }),
        ("Policies", {
            "fields": ("is_returnable", "is_exchangeable", "is_cod_available")
        }),
        ("SEO", {
            "fields": ("meta_title", "meta_description")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )

    def discount_display(self, obj):
        return f"{obj.discount_percent}%"
    
    discount_display.short_description = "Discount"

    def total_stock_display(self, obj):
        return obj.total_stock
    
    total_stock_display.short_description = "Total Stock"

    def in_stock_display(self, obj):
        if obj.in_stock:
            return format_html(
                '<span style="color:green; font-weight:600;">In Stock</span>'
            )
        return format_html(
            '<span style="color:red; font-weight:600;">Out of Stock</span>'
        )
    
    in_stock_display.short_description = "Stock Status"

# -------------------- PRODUCT IMAGE ADMIN -------------------- #
class ProductImageAdmin(RoleBasedAdminMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "image_preview",
        "is_primary",
        "sort_order",
        "created_at",
    )
    list_filter = ("is_primary", "created_at")
    search_fields = ("product__name", "alt_text", "image")
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:70px; width:70px; object-fit:cover; border-radius:6px;" />',
                obj.image.url,
            )
        return "No Image"
    image_preview.short_description = "Preview"

# -------------------- PRODUCT VARIANT ADMIN -------------------- #
class ProductVariantAdmin(RoleBasedAdminMixin, admin.ModelAdmin):
    list_display = (
        "product",
        "color",
        "size",
        "variant_sku",
        "stock",
        "reserved_stock",
        "available_stock_display",
        "is_active",
        "created_at",
    )
    list_filter = ("size", "color", "is_active", "created_at")
    search_fields = ("product__name", "variant_sku", "color", "size")
    readonly_fields = ("available_stock_display",)
    ordering = ("product", "color", "size")

    def available_stock_display(self, obj):
        return obj.available_stock
    
    available_stock_display.short_description = "Available Stock"

# -------------------- CART ADMIN -------------------- #
class CartItemAdmin(RoleBasedAdminMixin, admin.ModelAdmin):
    list_display = ("user", "product", "variant", "qty", "created_at")
    search_fields = (
        "user__email",
        "user__username",
        "product__name",
        "variant__variant_sku",
        "variant__color",
        "variant__size",
    )
    list_filter = ("created_at", "variant__size", "variant__color")
    ordering = ("-created_at",)

# -------------------- WISHLIST ADMIN -------------------- #
class WishlistItemAdmin(RoleBasedAdminMixin, admin.ModelAdmin):
    list_display = ("user", "product", "created_at")
    search_fields = ("user__email", "user__username", "product__name")
    list_filter = ("created_at",)
    ordering = ("-created_at",)

# -------------------- NOTIFICATION ADMIN -------------------- #
class AdminNotificationAdmin(RoleBasedAdminMixin, admin.ModelAdmin):
    list_display = (
        "title",
        "notification_type",
        "created_for",
        "read_count",
        "created_at",
    )
    list_filter = ("notification_type", "created_at")
    search_fields = ("title", "message", "created_for__email", "created_for__username")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(reads_count=Count("reads"))

    def read_count(self, obj):
        return obj.reads_count
    
    read_count.short_description = "Read Count"

class AdminNotificationReadAdmin(RoleBasedAdminMixin, admin.ModelAdmin):
    list_display = (
        "user",
        "notification",
        "read_at",
    )

    search_fields = (
        "user__email",
        "user__username",
        "notification__title",
    )

    list_filter = ("read_at",)
    readonly_fields = ("read_at",)
    ordering = ("-read_at",)

# -------------------- CUSTOM ADMIN SITE REGISTRATION -------------------- #
admin_site.register(ParentCategory, ParentCategoryAdmin)
admin_site.register(SubCategory, SubCategoryAdmin)
admin_site.register(ChildCategory, ChildCategoryAdmin)

admin_site.register(Brand, BrandAdmin)
admin_site.register(ProductTag, ProductTagAdmin)

admin_site.register(Product, ProductAdmin)
admin_site.register(ProductImage, ProductImageAdmin)
admin_site.register(ProductVariant, ProductVariantAdmin)
admin_site.register(Stock)
admin_site.register(Warehouse)

admin_site.register(CartItem, CartItemAdmin)
admin_site.register(WishlistItem, WishlistItemAdmin)

admin_site.register(AdminNotification, AdminNotificationAdmin)
admin_site.register(AdminNotificationRead, AdminNotificationReadAdmin)