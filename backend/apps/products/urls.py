from django.urls import include, path

from .views import (
    BrandListView,
    BrandDetailView,
    CartItemDetailView,
    CartItemListCreateView,
    CartSummaryView,
    CategoryListView,
    MegaMenuView,
    ProductDetailAPIView,
    ProductFilterMetaAPIView,
    ProductListAPIView,
    ProductTagListView,
    RelatedProductListView,
    WishlistCheckView,
    WishlistItemDetailView,
    WishlistItemListCreateView,
    export_products_csv,
    export_products_excel,
    export_products_pdf,
    
    ai_tag_analysis,
)

# =========================================================
# PRODUCT API ROUTES
# =========================================================
urlpatterns = [
    
    # PRODUCTS
    path(
        "",
        ProductListAPIView.as_view(),
        name="product_list",
    ),

    path(
        "menu/",
        MegaMenuView.as_view(),
        name="mega_menu",
    ),

    path(
        "filters/meta/",
        ProductFilterMetaAPIView.as_view(),
        name="product_filter_meta",
    ),

    path(
        "related/<slug:slug>/",
        RelatedProductListView.as_view(),
        name="related_products",
    ),

    # CATEGORY / BRAND / TAG
    path(
        "categories/",
        CategoryListView.as_view(),
        name="category_list",
    ),

    path(
        "brands/",
        BrandListView.as_view(),
        name="brand_list",
    ),

    path(
        "brands/<slug:slug>/",
        BrandDetailView.as_view(),
        name="brand_detail",
    ),

    path(
        "tags/",
        ProductTagListView.as_view(),
        name="tag_list",
    ),

    path(
        "ai-analysis/",
        ai_tag_analysis,
        name="ai_tag_analysis"
    ),

    # CART
    path(
        "cart/",
        CartItemListCreateView.as_view(),
        name="cart_list_create",
    ),

    path(
        "cart/summary/",
        CartSummaryView.as_view(),
        name="cart_summary",
    ),

    path(
        "cart/<int:pk>/",
        CartItemDetailView.as_view(),
        name="cart_detail",
    ),

    # WISHLIST
    path(
        "wishlist/",
        WishlistItemListCreateView.as_view(),
        name="wishlist_list_create",
    ),

    path(
        "wishlist/check/<int:product_id>/",
        WishlistCheckView.as_view(),
        name="wishlist_check",
    ),

    path(
        "wishlist/<int:pk>/",
        WishlistItemDetailView.as_view(),
        name="wishlist_detail",
    ),

    # ADMIN NOTIFICATIONS
    path(
        "",
        include("apps.products.notifications.urls"),
    ),

    # EXPORTS
    path(
        "admin/products/export/csv/",
        export_products_csv,
        name="export_products_csv",
    ),

    path(
        "admin/products/export/excel/",
        export_products_excel,
        name="export_products_excel",
    ),

    path(
        "admin/products/export/pdf/",
        export_products_pdf,
        name="export_products_pdf",
    ),

    # PRODUCT DETAIL
    # MUST ALWAYS BE LAST
    path(
        "<slug:slug>/",
        ProductDetailAPIView.as_view(),
        name="product_detail",
    ),
]