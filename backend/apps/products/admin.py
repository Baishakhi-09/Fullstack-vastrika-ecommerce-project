from django.contrib import admin
from django import forms
from django.db.models import Count
from django.utils.html import format_html

from vastrika_backend.admin_site import admin_site

from .models import (
    Brand,
    ParentCategory,
    SubCategory,
    ChildCategory,
    Product,
    ProductImage,
    ProductTag,
    ProductVariant,
    CartItem,
    WishlistItem,
    Stock,
    Warehouse,
)

from .notifications.models import (
    AdminNotification,
    AdminNotificationRead,
)


# =========================================================
# ROLE-BASED ADMIN MIXIN
# =========================================================

class RoleBasedAdminMixin:
    def _has_admin_access(self, request):
        return (
            request.user.is_authenticated
            and (
                request.user.is_superuser
                or getattr(request.user, "role", None) == "admin"
            )
        )

    def has_module_permission(self, request):
        return self._has_admin_access(request)

    def has_view_permission(self, request, obj=None):
        return request.user.is_authenticated

    def has_add_permission(self, request):
        return self._has_admin_access(request)

    def has_change_permission(self, request, obj=None):
        return self._has_admin_access(request)

    def has_delete_permission(self, request, obj=None):
        return self._has_admin_access(request)


# =========================================================
# PRODUCT ADMIN FORM
# =========================================================

class ProductAdminForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = "__all__"

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["sub_category"].queryset = (
            SubCategory.objects.none()
        )

        self.fields["child_category"].queryset = (
            ChildCategory.objects.none()
        )

        # Existing Product
        if self.instance and self.instance.pk:

            if self.instance.parent_category:

                self.fields["sub_category"].queryset = (
                    SubCategory.objects.filter(
                        parent_category=self.instance.parent_category,
                        is_active=True,
                    )
                )

            if self.instance.sub_category:

                self.fields["child_category"].queryset = (
                    ChildCategory.objects.filter(
                        sub_category=self.instance.sub_category,
                        is_active=True,
                    )
                )

        # Dynamic Parent Category
        if "parent_category" in self.data:

            try:
                parent_id = int(
                    self.data.get("parent_category")
                )

                self.fields["sub_category"].queryset = (
                    SubCategory.objects.filter(
                        parent_category_id=parent_id,
                        is_active=True,
                    )
                )

            except (TypeError, ValueError):
                pass

        # Dynamic Sub Category
        if "sub_category" in self.data:

            try:
                sub_id = int(
                    self.data.get("sub_category")
                )

                self.fields["child_category"].queryset = (
                    ChildCategory.objects.filter(
                        sub_category_id=sub_id,
                        is_active=True,
                    )
                )

            except (TypeError, ValueError):
                pass


# =========================================================
# PRODUCT IMAGE INLINE
# =========================================================

class ProductImageInline(admin.TabularInline):

    model = ProductImage

    extra = 1

    fields = (
        "image_preview",
        "image",
        "alt_text",
        "is_primary",
        "sort_order",
    )

    readonly_fields = (
        "image_preview",
    )

    ordering = ("sort_order",)

    def image_preview(self, obj):

        if obj and obj.image:

            return format_html(
                '''
                <img
                    src="{}"
                    style="
                        width:70px;
                        height:70px;
                        object-fit:cover;
                        border-radius:12px;
                        border:1px solid #e2e8f0;
                    "
                >
                ''',
                obj.image.url,
            )

        return format_html(
            '''
            <div
                style="
                    width:70px;
                    height:70px;
                    border-radius:12px;
                    background:#f1f5f9;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    color:#64748b;
                    font-size:11px;
                "
            >
                No Image
            </div>
            '''
        )

    image_preview.short_description = "Preview"


# =========================================================
# PRODUCT VARIANT INLINE
# =========================================================

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

    readonly_fields = (
        "available_stock_display",
    )

    def available_stock_display(self, obj):

        if obj and obj.pk:
            return obj.available_stock

        return 0

    available_stock_display.short_description = (
        "Available Stock"
    )


# =========================================================
# CATEGORY ADMINS
# =========================================================

class ParentCategoryAdmin(
    RoleBasedAdminMixin,
    admin.ModelAdmin,
):

    list_display = (
        "name",
        "is_active",
        "sort_order",
        "created_at",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
    )

    ordering = (
        "sort_order",
        "name",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }


class SubCategoryAdmin(
    RoleBasedAdminMixin,
    admin.ModelAdmin,
):

    list_display = (
        "name",
        "parent_category",
        "is_active",
        "sort_order",
        "created_at",
    )

    list_filter = (
        "is_active",
        "parent_category",
        "created_at",
    )

    search_fields = (
        "name",
        "parent_category__name",
    )

    ordering = (
        "parent_category__name",
        "sort_order",
        "name",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }


class ChildCategoryAdmin(
    RoleBasedAdminMixin,
    admin.ModelAdmin,
):

    list_display = (
        "name",
        "sub_category",
        "get_parent_category",
        "is_active",
        "sort_order",
        "created_at",
    )

    list_filter = (
        "is_active",
        "sub_category",
        "sub_category__parent_category",
        "created_at",
    )

    search_fields = (
        "name",
        "sub_category__name",
        "sub_category__parent_category__name",
    )

    ordering = (
        "sub_category__parent_category__name",
        "sub_category__name",
        "sort_order",
        "name",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }

    @admin.display(description="Parent Category")
    def get_parent_category(self, obj):

        if obj.sub_category:
            return obj.sub_category.parent_category

        return "-"


# =========================================================
# BRAND ADMIN
# =========================================================

class BrandAdmin(
    RoleBasedAdminMixin,
    admin.ModelAdmin,
):

    list_display = (
        "name",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
    )

    ordering = (
        "name",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }


# =========================================================
# PRODUCT TAG ADMIN
# =========================================================

class ProductTagAdmin(
    RoleBasedAdminMixin,
    admin.ModelAdmin,
):

    list_display = (
        "name",
        "slug",
    )

    search_fields = (
        "name",
    )

    ordering = (
        "name",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }


# =========================================================
# PRODUCT ADMIN
# =========================================================

class ProductAdmin(
    RoleBasedAdminMixin,
    admin.ModelAdmin,
):

    form = ProductAdminForm

    change_list_template = (
        "admin/products/change_list.html"
    )

    list_display = (
        "product_image",
        "display_name",
        "product_brand",
        "category_display",
        "product_selling_price",
        "product_mrp",
        "discount_badge",
        "stock_badge",
        "display_is_active",
        "display_is_featured",
        "display_created_at",
    )

    list_display_links = (
        "product_image",
        "display_name",
    )

    list_filter = (
        "is_active",
        "is_featured",
        "is_new_arrival",
        "is_best_seller",
        "gender",
        "brand",
        "parent_category",
        "created_at",
    )

    search_fields = (
        "name",
        "slug",
        "sku",
        "brand__name",
    )

    readonly_fields = (
        "slug",
        "sku",
        "discount_badge",
        "stock_badge",
        "created_at",
        "updated_at",
    )

    filter_horizontal = (
        "tags",
    )

    inlines = [
        ProductImageInline,
        ProductVariantInline,
    ]

    ordering = (
        "-created_at",
    )

    list_per_page = 20
    show_full_result_count = False

    list_select_related = (
        "brand",
        "parent_category",
        "sub_category",
        "child_category",
    )

    autocomplete_fields = (
        "brand",
        "parent_category",
        "sub_category",
        "child_category",
    )

    date_hierarchy = "created_at"
    empty_value_display = "-"
    save_as = True
    search_help_text = (
        "Search by product name, SKU, slug or brand."
    )

    save_on_top = True

    actions = (
        "mark_active",
        "mark_inactive",
        "mark_featured",
    )

    fieldsets = (

        ("Basic Information", {
            "fields": (
                "name",
                "slug",
                "sku",
                "brand",
                "tags",
            )
        }),

        ("Categories", {
            "fields": (
                "parent_category",
                "sub_category",
                "child_category",
            )
        }),

        ("Descriptions", {
            "fields": (
                "short_description",
                "description",
            )
        }),

        ("Attributes", {
            "fields": (
                "gender",
                "occasion",
            )
        }),

        ("Pricing", {
            "fields": (
                "mrp",
                "selling_price",
                "discount_badge",
            )
        }),

        ("Stock & Visibility", {
            "fields": (
                "stock_badge",
                "is_active",
                "is_featured",
                "is_new_arrival",
                "is_best_seller",
            )
        }),

        ("Policies", {
            "fields": (
                "is_returnable",
                "is_exchangeable",
                "is_cod_available",
            )
        }),

        ("SEO", {
            "fields": (
                "meta_title",
                "meta_description",
            )
        }),

        ("Timestamps", {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )

    def get_queryset(self, request):

        queryset = super().get_queryset(request)

        return queryset.select_related(
            "brand",
            "parent_category",
            "sub_category",
            "child_category",
        ).prefetch_related(
            "images",
            "variants",
            "tags",
        )

    class Media:

        css = {
            "all": (
                "admin/css/custom.css",
            )
        }

        js = (
            "admin/js/custom.js",
        )

    def changelist_view(
        self,
        request,
        extra_context=None,
    ):
        extra_context = extra_context or {}
        queryset = self.get_queryset(request)

        extra_context.update({

            "total_products":
                queryset.count(),

            "active_products":
                queryset.filter(
                    is_active=True
                ).count(),

            "featured_products":
                queryset.filter(
                    is_featured=True
                ).count(),

            "out_of_stock":
                queryset.filter(
                    variants__stock=0
                ).distinct().count(),
        })

        return super().changelist_view(
            request,
            extra_context=extra_context,
        )
    
    @admin.display(description="Name")
    def display_name(self, obj):
        return obj.name


    @admin.display(description="Is Active")
    def display_is_active(self, obj):
        return obj.is_active


    @admin.display(description="Is Featured")
    def display_is_featured(self, obj):
        return obj.is_featured


    @admin.display(description="Created At")
    def display_created_at(self, obj):
        return obj.created_at
    
    @admin.display(description="Brand")
    def product_brand(self, obj):

        if obj.brand:
            return obj.brand.name

        return "-"


    @admin.display(description="Selling Price")
    def product_selling_price(self, obj):
        return obj.selling_price


    @admin.display(description="MRP")
    def product_mrp(self, obj):
        return obj.mrp

    @admin.display(description="Image")
    def product_image(self, obj):

        primary_image = next(
            (
                image
                for image in obj.images.all()
                if image.is_primary
            ),
            None
        )

        if primary_image and primary_image.image:

            return format_html(
                '''
                <img
                    src="{}"
                    style="
                        width:60px;
                        height:60px;
                        object-fit:cover;
                        border-radius:14px;
                        border:1px solid #e2e8f0;
                    "
                >
                ''',
                primary_image.image.url,
            )

        return format_html(
            '''
            <div
                style="
                    width:60px;
                    height:60px;
                    border-radius:14px;
                    background:#f1f5f9;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    color:#64748b;
                    font-size:11px;
                "
            >
                No Image
            </div>
            '''
        )

    @admin.display(description="Category")
    def category_display(self, obj):

        categories = filter(None, [
            obj.parent_category,
            obj.sub_category,
            obj.child_category,
        ])

        return " → ".join(
            str(category)
            for category in categories
        )

    @admin.display(description="Discount")
    def discount_badge(self, obj):

        discount = obj.discount_percent

        if discount <= 0:
            color = "#64748b"

        elif discount <= 20:
            color = "#10b981"

        else:
            color = "#ef4444"

        return format_html(
            '''
            <span
                style="
                    background:{};
                    color:white;
                    padding:6px 12px;
                    border-radius:30px;
                    font-size:12px;
                    font-weight:600;
                "
            >
                {}%
            </span>
            ''',
            color,
            discount,
        )

    @admin.display(description="Stock")
    def stock_badge(self, obj):

        total_stock = obj.total_stock

        if total_stock <= 0:

            color = "#ef4444"
            label = "Out of Stock"

        elif total_stock <= 5:

            color = "#f59e0b"
            label = "Low Stock"

        else:

            color = "#10b981"
            label = "In Stock"

        return format_html(
            '''
            <span
                style="
                    background:{};
                    color:white;
                    padding:6px 12px;
                    border-radius:30px;
                    font-size:12px;
                    font-weight:600;
                "
            >
                {}
            </span>
            ''',
            color,
            label,
        )
    
    @admin.action(description="Mark selected products as Active")
    def mark_active(self, request, queryset):

        queryset.update(
            is_active=True
        )


    @admin.action(description="Mark selected products as Inactive")
    def mark_inactive(self, request, queryset):

        queryset.update(
            is_active=False
        )


    @admin.action(description="Mark selected products as Featured")
    def mark_featured(self, request, queryset):

        queryset.update(
            is_featured=True
        )


# =========================================================
# PRODUCT IMAGE ADMIN
# =========================================================

class ProductImageAdmin(
    RoleBasedAdminMixin,
    admin.ModelAdmin,
):

    list_display = (
        "id",
        "product",
        "image_preview",
        "is_primary",
        "sort_order",
        "created_at",
    )

    list_filter = (
        "is_primary",
        "created_at",
    )

    search_fields = (
        "product__name",
        "alt_text",
    )

    readonly_fields = (
        "image_preview",
    )

    ordering = (
        "-created_at",
    )

    def image_preview(self, obj):

        if obj.image:

            return format_html(
                '''
                <img
                    src="{}"
                    style="
                        width:70px;
                        height:70px;
                        object-fit:cover;
                        border-radius:12px;
                    "
                >
                ''',
                obj.image.url,
            )

        return "No Image"

    image_preview.short_description = "Preview"


# =========================================================
# PRODUCT VARIANT ADMIN
# =========================================================

class ProductVariantAdmin(
    RoleBasedAdminMixin,
    admin.ModelAdmin,
):

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

    list_filter = (
        "size",
        "color",
        "is_active",
        "created_at",
    )

    search_fields = (
        "product__name",
        "variant_sku",
    )

    readonly_fields = (
        "available_stock_display",
    )

    ordering = (
        "product",
        "color",
        "size",
    )

    def available_stock_display(self, obj):
        return obj.available_stock

    available_stock_display.short_description = (
        "Available Stock"
    )


# =========================================================
# CART ADMIN
# =========================================================

class CartItemAdmin(
    RoleBasedAdminMixin,
    admin.ModelAdmin,
):

    list_display = (
        "user",
        "product",
        "variant",
        "qty",
        "created_at",
    )

    ordering = (
        "-created_at",
    )


# =========================================================
# WISHLIST ADMIN
# =========================================================

class WishlistItemAdmin(
    RoleBasedAdminMixin,
    admin.ModelAdmin,
):

    list_display = (
        "user",
        "product",
        "created_at",
    )

    ordering = (
        "-created_at",
    )


# =========================================================
# NOTIFICATION ADMIN
# =========================================================

class AdminNotificationAdmin(
    RoleBasedAdminMixin,
    admin.ModelAdmin,
):

    list_display = (
        "title",
        "notification_type",
        "created_for",
        "read_count",
        "created_at",
    )

    ordering = (
        "-created_at",
    )

    def get_queryset(self, request):

        queryset = super().get_queryset(request)

        return queryset.annotate(
            reads_count=Count("reads")
        )

    def read_count(self, obj):
        return obj.reads_count

    read_count.short_description = "Read Count"


class AdminNotificationReadAdmin(
    RoleBasedAdminMixin,
    admin.ModelAdmin,
):

    list_display = (
        "user",
        "notification",
        "read_at",
    )

    ordering = (
        "-read_at",
    )


# =========================================================
# ADMIN REGISTRATION
# =========================================================

admin_site.register(
    ParentCategory,
    ParentCategoryAdmin,
)

admin_site.register(
    SubCategory,
    SubCategoryAdmin,
)

admin_site.register(
    ChildCategory,
    ChildCategoryAdmin,
)

admin_site.register(
    Brand,
    BrandAdmin,
)

admin_site.register(
    ProductTag,
    ProductTagAdmin,
)

admin_site.register(
    Product,
    ProductAdmin,
)

admin_site.register(
    ProductImage,
    ProductImageAdmin,
)

admin_site.register(
    ProductVariant,
    ProductVariantAdmin,
)

admin_site.register(
    Stock,
)

admin_site.register(
    Warehouse,
)

admin_site.register(
    CartItem,
    CartItemAdmin,
)

admin_site.register(
    WishlistItem,
    WishlistItemAdmin,
)

admin_site.register(
    AdminNotification,
    AdminNotificationAdmin,
)

admin_site.register(
    AdminNotificationRead,
    AdminNotificationReadAdmin,
)