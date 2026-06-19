from django import forms

from django.contrib import admin
from django.db import models
from django.db.models import Count, Sum
from django.utils.html import format_html
from django.urls import reverse

from vastrika_backend.admin_site import admin_site

from .forms import (
    ProductAdminForm, 
    BrandAdminForm, 
    ProductTagAdminForm, 
    ParentCategoryForm,
    SubCategoryForm,
    ChildCategoryForm,
    ProductVariantAdminForm,
    WarehouseAdminForm,
)

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

from apps.products.ai.seo_engine import (
    calculate_seo_score,
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
                or getattr(
                    request.user,
                    "role",
                    None,
                ) == "admin"
            )
        )

    def has_module_permission(
        self,
        request,
    ):
        return self._has_admin_access(request)

    def has_view_permission(
        self,
        request,
        obj=None,
    ):
        return request.user.is_authenticated

    def has_add_permission(
        self,
        request,
    ):
        return self._has_admin_access(request)

    def has_change_permission(
        self,
        request,
        obj=None,
    ):
        return self._has_admin_access(request)

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):
        return self._has_admin_access(request)
    
# =========================================================
# AUDIT ADMIN MIXIN
# =========================================================
    
class AuditAdminMixin:

    def save_model(
        self,
        request,
        obj,
        form,
        change
    ):
        if not obj.pk:
            obj.created_by = request.user

        obj.updated_by = request.user

        super().save_model(
            request,
            obj,
            form,
            change
        )

# =========================================================
# PRODUCT IMAGE INLINE
# =========================================================

class ProductImageInline(admin.StackedInline):

    model = ProductImage

    extra = 0

    verbose_name = "Product Image"
    verbose_name_plural = "Product Images"

    ordering = ("sort_order",)

    fields = (
        # "image_preview",
        "image",
        "alt_text",
        "image_type",
        "is_primary",
        "sort_order",
    )

    readonly_fields = ()

    @admin.display(description="")
    def image_preview(self, obj):

        if obj and obj.image:

            return format_html(
                """
                <img
                    src="{}"
                    class="admin-product-inline-image"
                >
                """,
                obj.image.url,
            )

        return format_html(
            """
            <div class="admin-no-image">
                No Image
            </div>
            """
        )


# =========================================================
# PRODUCT VARIANT INLINE
# =========================================================

class ProductVariantInline(admin.TabularInline):

    model = ProductVariant

    extra = 0

    verbose_name = "Product Variant"

    verbose_name_plural = "Product Variants"

    show_change_link = True

    fields = (
        "variant_name",
        "color",
        "size",
        "variant_sku",
        "stock",
        "reserved_stock",
        "damaged_quantity",
        "available_stock_display",
        "is_active",
    )

    readonly_fields = (
        "available_stock_display",
    )

    @admin.display(description="Available Stock")
    def available_stock_display(self, obj):

        if obj and obj.pk:
            return obj.available_stock

        return 0
    
# =========================================================
# PRODUCT VARIANT ADMIN
# =========================================================

class ProductVariantAdmin(
    AuditAdminMixin,
    RoleBasedAdminMixin,
    admin.ModelAdmin,
):
    form = ProductVariantAdminForm

    change_form_template = (
        "admin/products/productvariant/productvariant_form.html"
    )

    change_list_template = (
        "admin/products/productvariant/productvariant_list.html"
    )

    list_select_related = (
        "product",
    )

    list_display = (
        "product_name",
        "variant_name",
        "color",
        "size",
        "variant_sku",
        "stock",
        "reserved_stock",
        "damaged_quantity",
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
        "variant_name",
        "variant_sku", 
    )

    ordering = ( 
        "product", 
        "variant_name",
        "color", 
        "size", 
    )

    readonly_fields = (
        "available_stock_display",
    )

    @admin.display(description="Available Stock")
    def available_stock_display(self, obj):
        if obj:
            return obj.available_stock
        return 0
    
    @admin.display(description="Product")
    def product_name(self, obj): 
        return obj.product.name

    def changeform_view(
        self,
        request,
        object_id=None,
        form_url="",
        extra_context=None,
    ):

        extra_context = extra_context or {}

        if object_id:
            variant = self.get_object(
                request,
                object_id
            )

            if variant:
                available_stock = variant.available_stock

                if available_stock <= 0:
                    inventory_status = "Out of Stock"

                    inventory_class = "status-danger"

                elif available_stock <= 5:
                    inventory_status = "Low Stock"

                    inventory_class = "status-warning"

                else:
                    inventory_status = "In Stock"

                    inventory_class = "status-success"

                extra_context.update({

                    "inventory_status":
                        inventory_status,

                    "inventory_class":
                        inventory_class,

                    "available_stock":
                        available_stock,

                })

        return super().changeform_view(
            request,
            object_id,
            form_url,
            extra_context,
        )

    actions = [
        "delete_selected_productvariant"
    ]

    def get_actions(
        self,
        request
    ):
        actions = super().get_actions(request)

        # Remove delete action
        if "delete_selected" in actions:
            del actions["delete_selected"]

        return actions

    @admin.action(
        description="Delete selected productvariant"
    )
    def delete_selected_productvariant(
        self,
        request,
        queryset
    ):
        total_deleted = queryset.count()

        queryset.delete()

        self.message_user(
            request,
            f"{total_deleted} productvariant(s) deleted successfully."
        )

    def changelist_view(
        self,
        request,
        extra_context=None,
    ):

        extra_context = extra_context or {}

        queryset = ProductVariant.objects.all()

        total_variants = queryset.count()

        active_variants = queryset.filter(
            is_active=True
        ).count()

        low_stock_variants = sum(
            1
            for variant in queryset
            if 0 < variant.available_stock <= 5
        )

        out_of_stock_variants = sum(
            1
            for variant in queryset
            if variant.available_stock == 0
        )

        extra_context.update({

            "total_variants":
                total_variants,

            "active_variants":
                active_variants,

            "low_stock_variants":
                low_stock_variants,

            "out_of_stock_variants":
                out_of_stock_variants,

        })

        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )

        if hasattr(response, "context_data"):

            action_form = response.context_data.get(
                "action_form"
            )

            if action_form:
                action_form.fields[
                    "action"
                ].widget.attrs.update({
                    "id": "id_action"
                })

        return response

# =========================================================
# CATEGORY ADMINS
# =========================================================

class ParentCategoryAdmin(
    AuditAdminMixin,
    RoleBasedAdminMixin,
    admin.ModelAdmin,
):
    form = ParentCategoryForm

    list_display = (
        "name",
        "status",
        "is_featured",
        "view_count",
        "sort_order",
        "created_at",
    )

    list_filter = (
        "status",
        "is_featured",
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

    change_form_template = (
        "admin/products/parentcategory/parentcategory_form.html"
    )

    actions = [
        "delete_selected_parentcategories"
    ]

    def get_actions(
        self,
        request
    ):
        actions = super().get_actions(request)

        # Remove delete action
        if "delete_selected" in actions:
            del actions["delete_selected"]

        return actions

    @admin.action(
        description="Delete selected categories"
    )
    def delete_selected_parentcategories(
        self,
        request,
        queryset
    ):
        total_deleted = queryset.count()

        queryset.delete()

        self.message_user(
            request,
            f"{total_deleted} category(s) deleted successfully."
        )

    def changelist_view(
        self,
        request,
        extra_context=None
    ):
        extra_context = extra_context or {}

        extra_context["total_categories"] = (
            ParentCategory.objects.count()
        )

        extra_context["published_categories"] = (
            ParentCategory.objects.filter(
                status="published"
            ).count()
        )

        extra_context["featured_categories"] = (
            ParentCategory.objects.filter(
                is_featured=True
            ).count()
        )

        extra_context["draft_categories"] = (
            ParentCategory.objects.filter(
                status="draft"
            ).count()
        )

        response = super().changelist_view(
            request,
            extra_context=extra_context
        )

        if hasattr(response, "context_data"):

            action_form = response.context_data.get(
                "action_form"
            )

            if action_form:
                action_form.fields[
                    "action"
                ].widget.attrs.update({
                    "id": "id_action"
                })

        return response


class SubCategoryAdmin(
    AuditAdminMixin,
    RoleBasedAdminMixin,
    admin.ModelAdmin,
):

    form = SubCategoryForm

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

    change_form_template = (
        "admin/products/subcategory/subcategory_form.html"
    )

    change_list_template = (
        "admin/products/subcategory/subcategory_list.html"
    )

    actions = [
        "delete_selected_subcategories"
    ]

    def get_actions(
        self,
        request
    ):
        actions = super().get_actions(request)

        # Remove delete action
        if "delete_selected" in actions:
            del actions["delete_selected"]

        return actions

    @admin.action(
        description="Delete selected categories"
    )
    def delete_selected_subcategories(
        self,
        request,
        queryset
    ):
        total_deleted = queryset.count()

        queryset.delete()

        self.message_user(
            request,
            f"{total_deleted} category(s) deleted successfully."
        )

    def changelist_view(
        self,
        request,
        extra_context=None
    ):
        extra_context = extra_context or {}

        extra_context["total_subcategories"] = (
            SubCategory.objects.count()
        )

        extra_context["active_subcategories"] = (
            SubCategory.objects.filter(
                is_active=True
            ).count()
        )

        extra_context["inactive_subcategories"] = (
            SubCategory.objects.filter(
                is_active=False
            ).count()
        )

        extra_context["total_parents"] = (
            ParentCategory.objects.count()
        )

        response = super().changelist_view(
            request,
            extra_context=extra_context
        )

        if hasattr(response, "context_data"):
            action_form = response.context_data.get(
                "action_form"
            )

            if action_form:
                action_form.fields[
                    "action"
                ].widget.attrs.update({
                    "id": "id_action"
                })

        return response


class ChildCategoryAdmin(
    AuditAdminMixin,
    RoleBasedAdminMixin,
    admin.ModelAdmin,
):
    form = ChildCategoryForm
    
    change_form_template = (
        "admin/products/childcategory/childcategory_form.html"
    )

    change_list_template = (
        "admin/products/childcategory/childcategory_list.html"
    )

    list_display = (
        "name",
        "get_parent_category",
        "sub_category",
        "sort_order",
        "is_active",
    )

    search_fields = (
        "name",
        "slug",
        "sub_category__name",
    )

    list_filter = (
        "is_active",
        "sub_category",
    )

    ordering = (
        "sub_category",
        "sort_order",
        "name",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }

    fieldsets = ()
    
    actions = [
        "delete_selected_childcategories"
    ]

    @admin.display(description="Parent Category")
    def get_parent_category(self, obj):

        return (
            obj.sub_category.parent_category
            if obj.sub_category
            else "-"
        )

    def get_actions(
        self,
        request
    ):
        actions = super().get_actions(
            request
        )

        actions.pop(
            "delete_selected",
            None
        )

        return actions

    @admin.action(
        description="Delete selected child categories"
    )
    def delete_selected_childcategories(
        self,
        request,
        queryset
    ):
        total_deleted = queryset.count()

        for obj in queryset:
            obj.delete()

        self.message_user(
            request,
            f"{total_deleted} child category(s) deleted successfully."
        )

    def changelist_view(
        self,
        request,
        extra_context=None
    ):
        extra_context = extra_context or {}

        queryset = ChildCategory.objects.all()

        extra_context.update(
            {
                "total_categories":
                    queryset.count(),

                "active_categories":
                    queryset.filter(
                        is_active=True
                    ).count(),

                "draft_categories":
                    queryset.filter(
                        is_active=False
                    ).count(),

                "total_products":
                    0,  # replace later with real relation
            }
        )

        response = super().changelist_view(
            request,
            extra_context=extra_context
        )

        if hasattr(response, "context_data"):
            action_form = response.context_data.get(
                "action_form"
            )

            if action_form:
                action_form.fields[
                    "action"
                ].widget.attrs.update({
                    "id": "id_action"
                })

        return response


# =========================================================
# BRAND ADMIN
# =========================================================

class BrandAdmin(
    AuditAdminMixin,
    RoleBasedAdminMixin,
    admin.ModelAdmin,
):
    form = BrandAdminForm

    formfield_overrides = {
        models.CharField: {
            "widget": forms.TextInput(
                attrs={
                    "autocomplete": "off"
                }
            )
        }
    }

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

    change_form_template = (
        "admin/products/brand/change_form.html"
    )

    actions = ["delete_selected_brands"]

    @admin.action(
        description="Delete selected brands"
    )
    def delete_selected_brands(
        self,
        request,
        queryset
    ):

        total_deleted = queryset.count()

        queryset.delete()

        self.message_user(
            request,
            f"{total_deleted} brand(s) deleted successfully."
        )

    def get_actions(
        self,
        request
    ):

        actions = super().get_actions(request)

        if "delete_selected" in actions:
            del actions["delete_selected"]

        return actions


# =========================================================
# PRODUCT TAG ADMIN
# =========================================================

class ProductTagAdmin(
    AuditAdminMixin,
    RoleBasedAdminMixin,
    admin.ModelAdmin,
):
    form = ProductTagAdminForm

    list_display = (
        "name",
        "slug",
    )

    list_filter = (
        "status",
        "visibility",
        "is_featured",
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

    change_form_template = (
        "admin/products/producttag/change_form.html"
    )

    actions = [ "delete_selected_product_tags" ]

    @admin.action(
        description="Delete selected product tags"
    )
    def delete_selected_product_tags(
        self,
        request,
        queryset,
    ):
        total_deleted = queryset.count()

        queryset.delete()

        self.message_user(
            request,
            f"{total_deleted} product tag(s) deleted successfully."
        )

    def get_actions(
        self,
        request
    ):

        actions = super().get_actions(request)

        if "delete_selected" in actions:
            del actions["delete_selected"]

        return actions

    def changelist_view(
        self,
        request,
        extra_context=None,
    ):

        extra_context = extra_context or {}

        queryset = self.get_queryset(request)

        extra_context.update({

            "published_count":
                queryset.filter(
                    status="published"
                ).count(),

            "featured_count":
                queryset.filter(
                    is_featured=True
                ).count(),

            "archived_count":
                queryset.filter(
                    status="archived"
                ).count(),

        })

        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )

        if hasattr(response, "context_data"):

            action_form = response.context_data.get(
                "action_form"
            )

            if action_form:

                action_form.fields[
                    "action"
                ].widget.attrs.update({

                    "id": "id_action"

                })

        return response

    def changeform_view(
        self,
        request,
        object_id=None,
        form_url="",
        extra_context=None,
    ):
        extra_context = (
            extra_context or {}
        )

        seo_score = 0

        optimization_score = 0

        associated_products_count = 0

        search_visibility = (
            "Low Visibility"
        )

        visibility_status = (
            "Needs Improvement"
        )

        if object_id:

            product_tag = self.get_object(
                request,
                object_id,
            )

            if product_tag:

                seo_score = (
                    calculate_seo_score(

                        product_tag.name,

                        getattr(
                            product_tag,
                            "description",
                            "",
                        ),

                    )
                )

                optimization_score = (
                    seo_score
                )

                try:

                    associated_products_count = (
                        Product.objects.filter(
                            tags=product_tag
                        ).count()
                    )

                except Exception:

                    associated_products_count = 0

                if seo_score >= 80:

                    search_visibility = (
                        "High Visibility"
                    )

                    visibility_status = (
                        "Optimized"
                    )

                elif seo_score >= 50:

                    search_visibility = (
                        "Medium Visibility"
                    )

                    visibility_status = (
                        "Average"
                    )

                else:

                    search_visibility = (
                        "Low Visibility"
                    )

                    visibility_status = (
                        "Needs Improvement"
                    )

        extra_context.update({

            "seo_score":
                seo_score,

            "optimization_score":
                optimization_score,

            "search_visibility":
                search_visibility,

            "visibility_status":
                visibility_status,

            "associated_products_count":
                associated_products_count,

        })

        return super().changeform_view(
            request,
            object_id,
            form_url,
            extra_context,
        )
         

# =========================================================
# PRODUCT ADMIN
# =========================================================

class ProductAdmin(
    AuditAdminMixin,
    RoleBasedAdminMixin,
    admin.ModelAdmin,
):
    form = ProductAdminForm

    change_list_template = (
        "admin/products/product/product_list.html"
    )

    change_form_template = (
        "admin/products/product/product_form.html"
    )

    autocomplete_fields = [
        "tags",
    ]

    inlines = [
        ProductImageInline,
        ProductVariantInline,
    ]

    def get_form(
        self,
        request,
        obj=None,
        **kwargs
    ):
        form = super().get_form(
            request,
            obj,
            **kwargs
        )

        form.label_suffix = ""

        return form

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
        "edit_product",
    )

    list_display_links = None

    @admin.display(description="Actions")
    def edit_product(self, obj):

        return format_html(
            """
            <a
                href="{}"
                class="admin-edit-btn"
            >
                <span class="edit-btn-text">
                    Edit
                </span>
            </a>
            """,
            reverse(
                "admin:products_product_change",
                args=[obj.pk]
            )
        )

    list_filter = (
        "status",
        "is_active",
        "is_featured",
        "is_new_arrival",
        "is_best_seller",
        "gender",
        "brand",
        "child_category",
        "created_at",
    )

    search_fields = (
        "name",
        "slug",
        "sku",
        "brand__name",
    )

    readonly_fields = (
        "discount_badge",
        "stock_badge",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 20

    show_full_result_count = False

    list_select_related = (
        "brand",
        "child_category",
    )

    date_hierarchy = "created_at"

    empty_value_display = "-"

    save_as = True

    save_on_top = True

    search_help_text = (
        "Search by product name, SKU, slug or brand."
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
                # "parent_category",
                # "sub_category",
                "child_category",
            )
        }),

        ("Descriptions", {
            "fields": (
                "short_description",
                "description",
            )
        }),

        ("Media", {
            "fields": (
                "video",
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
                "cost_price",
                "tax",
                "discount_badge",
            )
        }),

        ("Stock & Visibility", {
            "fields": (
                "status",

                "barcode",
                "allow_backorders",

                "is_active",
                "is_featured",
                "is_best_seller",

                "stock_badge",
            )
        }),

        ("Shipping", {
            "fields": (
                "weight",
                "shipping_class",
                "length",
                "width",
                "height",
                "delivery_time",
                "free_shipping",
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
                "og_image",
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
            # "parent_category",
            # "sub_category",
            "child_category",
        ).prefetch_related(
            "images",
            "variants",
            "tags",
        )

    def calculate_seo_score(self, product):
        score = 0

        if product.meta_title:
            score += 20

        if (
            product.meta_title and
            50 <= len(product.meta_title) <= 60
        ):
            score += 10

        if product.meta_description:
            score += 20

        if (
            product.meta_description and
            140 <= len(product.meta_description) <= 160
        ):
            score += 10

        if product.slug:
            score += 15

        if product.og_image:
            score += 15

        if product.description:
            score += 10

        return min(score, 100)
    
    actions = [
        "delete_selected_product",
        "mark_active",
        "mark_inactive",
        "mark_featured",
    ]

    def get_actions(
        self,
        request
    ):
        actions = super().get_actions(request)

        if "delete_selected" in actions:
            del actions["delete_selected"]

        return actions
    
    @admin.action(
        description="Delete selected product"
    )

    def delete_selected_product(
        self,
        request,
        queryset
    ):
        total_deleted = queryset.count()

        queryset.delete()

        self.message_user(
            request,
            f"{total_deleted} product(s) deleted successfully."
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

        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )

        if hasattr(response, "context_data"):
            action_form = response.context_data.get(
                "action_form"
            )

            if action_form:
                action_form.fields[
                    "action"
                ].widget.attrs.update({
                    "id": "id_action"
                })

        return response

    def changeform_view(
        self,
        request,
        object_id=None,
        form_url="",
        extra_context=None,
    ):

        extra_context = extra_context or {}

        seo_score = 0

        if object_id:

            product = self.get_object(
                request,
                object_id,
            )

            if product:
                gallery_assets = product.images.count()

                video_count = 1 if product.video else 0

                storefront_ready = (
                    gallery_assets > 0
                )

                last_image = (
                    product.images.order_by("-created_at").first()
                )

                last_media_upload = (
                    last_image.created_at.strftime("%d %b %Y")
                    if last_image
                    else "—"
                )

                if gallery_assets >= 5:
                    media_score = 100

                elif gallery_assets >= 3:
                    media_score = 75

                elif gallery_assets >= 1:
                    media_score = 50

                else:
                    media_score = 0

                total_stock = sum(
                    variant.stock
                    for variant in product.variants.all()
                )

                reserved_stock = sum(
                    variant.reserved_stock
                    for variant in product.variants.all()
                )

                damaged_stock = sum(
                    variant.damaged_quantity
                    for variant in product.variants.all()
                )

                available_stock = sum(
                    variant.available_stock
                    for variant in product.variants.all()
                )

                if total_stock > 0:
                    reserved_percentage = round(
                        (reserved_stock / total_stock) * 100,
                        2
                    )

                    availability_percentage = round(
                        (available_stock / total_stock) * 100,
                        2
                    )

                    damage_percentage = round(
                        (damaged_stock / total_stock) * 100,
                        2
                    ) if total_stock > 0 else 0

                else:
                    reserved_percentage = 0
                    availability_percentage = 0

                inventory_value = sum(
                    variant.stock * product.selling_price
                    for variant in product.variants.all()
                )

                warehouse_stock = Stock.objects.filter(
                    product_variant__product=product
                ).select_related("warehouse").first()

                warehouse_status = (
                    warehouse_stock.warehouse.name
                    if warehouse_stock and warehouse_stock.warehouse
                    else "Unassigned"
                )

                warehouse_status_class = (
                    "status-success"
                    if warehouse_stock and warehouse_stock.warehouse
                    else "status-warning"
                )

                if available_stock <= 0:
                    stock_status = "Out Of Stock"
                    stock_status_class = "status-danger"

                elif available_stock <= 10:
                    stock_status = "Low Stock"
                    stock_status_class = "status-warning"

                else:
                    stock_status = "In Stock"
                    stock_status_class = "status-success"


                if warehouse_stock and warehouse_stock.warehouse:
                    fulfillment_status = "Ready"
                    fulfillment_status_class = "status-success"
                else:
                    fulfillment_status = "Pending"
                    fulfillment_status_class = "status-warning"


                if available_stock <= 10:
                    reorder_status = "Reorder Required"
                    reorder_status_class = "status-danger"
                else:
                    reorder_status = "Monitoring"
                    reorder_status_class = "status-success"

                extra_context["warehouse_status"] = warehouse_status

                extra_context["warehouse_status_class"] = (
                    warehouse_status_class
                )

                variant_count = product.variants.count()

                active_variant_count = product.variants.filter(
                    is_active=True
                ).count()

                out_of_stock_variant_count = product.variants.filter(
                    stock__lte=0
                ).count()

                if available_stock <= 0:
                    inventory_score = 0

                elif damaged_stock > available_stock:
                    inventory_score = 40

                elif damaged_stock > 0:
                    inventory_score = 75

                else:
                    inventory_score = 100

                seo_score = self.calculate_seo_score(
                    product
                )

                # SEO Status
                if seo_score >= 80:
                    seo_status = "Excellent"
                    seo_status_class = "success"

                elif seo_score >= 50:
                    seo_status = "Good"
                    seo_status_class = "warning"

                else:
                    seo_status = "Poor"
                    seo_status_class = "danger"

                # Media status
                if media_score >= 80:
                    media_status = "Excellent"
                    media_status_class = "success"

                elif media_score >= 50:
                    media_status = "Good"
                    media_status_class = "warning"

                else:
                    media_status = "Poor"
                    media_status_class = "danger"

                product_health_score = seo_score

                # commerce score
                commerce_score = round(
                    (
                        media_score +
                        seo_score +
                        inventory_score
                    ) / 3
                )

                # Commerce Status
                if commerce_score >= 80:
                    commerce_status = "Ready"
                    commerce_status_class = "success"

                elif commerce_score >= 50:
                    commerce_status = "Average"
                    commerce_status_class = "warning"

                else:
                    commerce_status = "Poor"
                    commerce_status_class = "danger"

                health_message = (
                    "Product is ready for sale"
                    if commerce_score >= 80
                    else "Needs optimization"
                )

                inventory_status = stock_status
                inventory_status_class = stock_status_class

                product_views = 0

                order_count = getattr(
                    product,
                    "order_count",
                    0
                )

                revenue = order_count * product.selling_price

                # Conversion Rate
                if product_views > 0:
                    conversion_rate = round(
                        (order_count / product_views) * 100,
                        2
                    )
                else:
                    conversion_rate = 0

                extra_context.update({

                    "gallery_count":
                        gallery_assets,

                    "video_count":
                        video_count,

                    "storefront_readiness":
                        "Yes" if storefront_ready else "No",

                    "media_score":
                        media_score,

                    "last_media_upload":
                        last_media_upload,

                    "total_stock":
                        total_stock,

                    "reserved_stock":
                        reserved_stock,

                    "available_stock":
                        available_stock,

                    "inventory_value":
                        inventory_value,

                    "stock_status":
                        stock_status,

                    "stock_status_class":
                        stock_status_class,

                    "fulfillment_status":
                        fulfillment_status,

                    "fulfillment_status_class":
                        fulfillment_status_class,

                    "reorder_status":
                        reorder_status,

                    "reorder_status_class":
                        reorder_status_class,

                    "reserved_percentage":
                        reserved_percentage,

                    "availability_percentage":
                        availability_percentage,

                    "inventory_score":
                        inventory_score,

                    "commerce_score":
                        commerce_score,

                    "variant_count":
                        variant_count,

                    "active_variant_count":
                        active_variant_count,

                    "out_of_stock_variant_count":
                        out_of_stock_variant_count,

                    "health_message":
                        health_message,

                    "seo_status":
                        seo_status,

                    "seo_status_class":
                        seo_status_class,

                    "media_status":
                        media_status,

                    "media_status_class":
                        media_status_class,

                    "commerce_status":
                        commerce_status,

                    "commerce_status_class":
                        commerce_status_class,

                    "inventory_status":
                        inventory_status,

                    "inventory_status_class":
                        inventory_status_class,

                    "product_views":
                        product_views,

                    "order_count":
                        order_count,

                    "revenue":
                        revenue,

                    "conversion_rate":
                        conversion_rate,

                    "damaged_stock":
                        damaged_stock,

                    "damage_percentage":
                        damage_percentage,
                })

                preview_url = (
                    f"{request.scheme}://{request.get_host()}"
                    f"/products/{product.slug}/"
                )

                extra_context["preview_url"] = preview_url

                extra_context["product_health_score"] = (
                    product_health_score
                )

                if product.status == "published":
                    extra_context["publishing_status"] = "Published"
                    extra_context["publishing_status_class"] = "success"
                else:
                    extra_context["publishing_status"] = "Draft"
                    extra_context["publishing_status_class"] = "warning"
            
            extra_context["seo_score"] = seo_score

        return super().changeform_view(
            request,
            object_id,
            form_url,
            extra_context,
        )

    @admin.display(description="Name")
    def display_name(self, obj):
        return obj.name

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

    @admin.display(description="Is Active")
    def display_is_active(self, obj):
        return obj.is_active

    @admin.display(description="Is Featured")
    def display_is_featured(self, obj):
        return obj.is_featured

    @admin.display(description="Created At")
    def display_created_at(self, obj):
        return obj.created_at

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
                """
                <img
                    src="{}"
                    class="admin-product-image"
                >
                """,
                primary_image.image.url,
            )

        return format_html(
            """
            <div class="admin-no-image">
                No Image
            </div>
            """
        )

    @admin.display(description="Category")
    def category_display(self, obj):

        if obj.child_category:
            return obj.child_category.name

        return "-"

    @admin.display(description="Discount")
    def discount_badge(self, obj):

        discount = obj.discount_percent

        if discount <= 0:
            badge_class = "badge-secondary"

        elif discount <= 20:
            badge_class = "badge-success"

        else:
            badge_class = "badge-danger"

        return format_html(
            """
            <span class="admin-badge {}">
                {}%
            </span>
            """,
            badge_class,
            discount,
        )

    @admin.display(description="Stock")
    def stock_badge(self, obj):

        total_stock = obj.total_stock

        if total_stock <= 0:

            badge_class = "badge-danger"
            label = "Out of Stock"

        elif total_stock <= 5:

            badge_class = "badge-warning"
            label = "Low Stock"

        else:

            badge_class = "badge-success"
            label = "In Stock"

        return format_html(
            """
            <span class="admin-badge {}">
                {}
            </span>
            """,
            badge_class,
            label,
        )

    @admin.action(
        description="Mark selected products as Active"
    )
    def mark_active(self, request, queryset):

        queryset.update(
            is_active=True
        )

    @admin.action(
        description="Mark selected products as Inactive"
    )
    def mark_inactive(self, request, queryset):

        queryset.update(
            is_active=False
        )

    @admin.action(
        description="Mark selected products as Featured"
    )
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
        "image",
        "image_type",
        "alt_text",
        "is_primary",
        "sort_order",
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

    @admin.display(description="")
    def image_preview(self, obj):

        if obj.image:

            return format_html(
                """
                <img
                    src="{}"
                    class="admin-product-inline-image"
                >
                """,
                obj.image.url,
            )

        return "No Image"

# =========================================================
# STOCK ADMIN
# =========================================================

class StockAdmin(
    AuditAdminMixin,
    RoleBasedAdminMixin,
    admin.ModelAdmin,
):
    change_form_template = (
        "admin/products/stock/stock_form.html"
    )

    change_list_template = (
        "admin/products/stock/stock_list.html"
    )

    list_display = (
        "product_variant",
        "warehouse",
        "quantity",
    )

    search_fields = (
        "product_variant__variant_sku",
        "warehouse__name",
    )

    fieldsets = ()

    def get_queryset(
        self,
        request,
    ):
        queryset = (
            super()
            .get_queryset(request)
            .select_related(
                "product_variant",
                "warehouse",
            )
        )

        status = request.GET.get(
            "status"
        )

        if status == "in_stock":

            queryset = queryset.filter(
                quantity__gt=10
            )

        elif status == "low_stock":

            queryset = queryset.filter(
                quantity__gt=0,
                quantity__lte=10
            )

        elif status == "out_stock":

            queryset = queryset.filter(
                quantity=0
            )

        warehouse = request.GET.get(
            "warehouse"
        )

        if warehouse:

            queryset = queryset.filter(
                warehouse_id=warehouse
            )

        return queryset

    def changeform_view(
        self,
        request,
        object_id=None,
        form_url="",
        extra_context=None,
    ):
        extra_context = extra_context or {}

        available_stock = 0

        warehouse_status = "Pending"
        warehouse_status_class = "status-pending"

        if object_id:
            stock = self.get_object(
                request,
                object_id
            )

            if stock:
                available_stock = stock.quantity

                if stock and stock.warehouse:
                    warehouse_status = stock.warehouse.name
                    warehouse_status_class = "status-success"

        inventory_status = "Out Of Stock"
        inventory_status_class = "status-out-stock"

        if available_stock > 10:
            inventory_status = "In Stock"
            inventory_status_class = "status-in-stock"

        elif available_stock > 0:
            inventory_status = "Low Stock"
            inventory_status_class = "status-low-stock"

        extra_context.update({
            "total_stock":
                Stock.objects.count(),

            "warehouse_count":
                Warehouse.objects.count(),

            "low_stock_count":
                Stock.objects.filter(
                    quantity__lte=5
                ).count(),

            "out_of_stock_count":
                Stock.objects.filter(
                    quantity=0
                ).count(),

            "current_stock":
                available_stock,

            "reserved_stock":
                0,

            "available_stock":
                available_stock,

            "inventory_status":
                inventory_status,

            "inventory_status_class":
                inventory_status_class,

            "warehouse_status": 
                warehouse_status,
            
            "warehouse_status_class": 
                warehouse_status_class,
        })

        return super().changeform_view(
            request,
            object_id,
            form_url,
            extra_context,
        )
    
    def changelist_view(
        self,
        request,
        extra_context=None,
    ):
        extra_context = extra_context or {}

        extra_context.update({

            "total_stock_count":
                Stock.objects.count(),

            "in_stock_count":
                Stock.objects.filter(
                    quantity__gt=10
                ).count(),

            "low_stock_count":
                Stock.objects.filter(
                    quantity__lte=10,
                    quantity__gt=0
                ).count(),

            "warehouse_count":
                Warehouse.objects.count(),

            "warehouses":
                Warehouse.objects.all(),

        })

        return super().changelist_view(
            request,
            extra_context=extra_context,
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

    list_select_related = (
        "user",
        "product",
        "variant",
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

    list_select_related = (
        "user",
        "product",
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

    @admin.display(description="Read Count")
    def read_count(self, obj):
        return obj.reads_count


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
# WAREHOUSE
# =========================================================

class WarehouseAdmin(
    AuditAdminMixin,
    RoleBasedAdminMixin,
    admin.ModelAdmin,
):
    form = WarehouseAdminForm

    change_form_template = (
        "admin/products/warehouse/warehouse_form.html"
    )

    change_list_template = (
        "admin/products/warehouse/warehouse_list.html"
    )

    list_display = (
        "name",
        "location",
        "contact_person",
        "manager_name",
        "phone",
        "shipping_zone",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "code",
        "location",
        "phone",
        "contact_person",
        "manager_name",
        "fulfillment_center",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    ordering = (
        "name",
    )

    @admin.display(description="Status")
    def warehouse_status(self, obj):

        if obj.is_active:
            return "Active"

        return "Inactive"
    
    actions = [
        "delete_selected_warehouse"
    ]

    def get_actions(
        self,
        request
    ):
        actions = super().get_actions(request)

        # Remove delete action
        if "delete_selected" in actions:
            del actions["delete_selected"]

        return actions

    @admin.action(
        description="Delete selected warehouse"
    )
    def delete_selected_warehouse(
        self,
        request,
        queryset
    ):
        total_deleted = queryset.count()

        queryset.delete()

        self.message_user(
            request,
            f"{total_deleted} warehouse(s) deleted successfully."
        )

    def changelist_view(
        self,
        request,
        extra_context=None,
    ):

        extra_context = extra_context or {}

        queryset = Warehouse.objects.all()

        total_warehouses = queryset.count()

        active_warehouses = queryset.filter(
            is_active=True
        ).count()

        inactive_warehouses = queryset.filter(
            is_active=False
        ).count()

        locations_covered = queryset.exclude(
            location=""
        ).count()

        extra_context.update({

            "total_warehouses":
                total_warehouses,

            "active_warehouses":
                active_warehouses,

            "inactive_warehouses":
                inactive_warehouses,

            "locations_covered":
                locations_covered,

        })

        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )

        if hasattr(response, "context_data"):

            action_form = response.context_data.get(
                "action_form"
            )

            if action_form:
                action_form.fields[
                    "action"
                ].widget.attrs.update({
                    "id": "id_action"
                })

        return response

    def changeform_view(
        self,
        request,
        object_id=None,
        form_url="",
        extra_context=None,
    ):
        extra_context = extra_context or {}

        if object_id:

            warehouse = self.get_object(
                request,
                object_id
            )

            warehouse_stocks = Stock.objects.filter(
                warehouse=warehouse
            )

            total_variants = warehouse_stocks.count()

            total_stock = (
                warehouse_stocks.aggregate(
                    total=Sum(
                        "product_variant__stock"
                    )
                )["total"] or 0
            )

            reserved_stock = (
                warehouse_stocks.aggregate(
                    total=Sum(
                        "product_variant__reserved_stock"
                    )
                )["total"] or 0
            )

            damaged_quantity = (
                warehouse_stocks.aggregate(
                    total=Sum(
                        "product_variant__damaged_quantity"
                    )
                )["total"] or 0
            )

            available_stock = (
                total_stock
                - reserved_stock
                - damaged_quantity
            )

            extra_context.update({
                "total_variants": 
                    total_variants,

                "total_stock": 
                    total_stock,

                "reserved_stock": 
                    reserved_stock,

                "damaged_quantity": 
                    damaged_quantity,

                "available_stock": 
                    available_stock,
            })

        return super().changeform_view(
            request,
            object_id,
            form_url,
            extra_context,
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
    StockAdmin,
)

admin_site.register(
    Warehouse,
    WarehouseAdmin,
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