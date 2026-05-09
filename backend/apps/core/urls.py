# =========================================================
# backend/apps/core/urls.py
# =========================================================

from django.urls import path

from .views import (
    DashboardProductListView,
    ProductSearchView,
)

app_name = "core"

urlpatterns = [

    # =====================================================
    # DASHBOARD PRODUCTS
    # =====================================================

    path(
        "products/",
        DashboardProductListView.as_view(),
        name="dashboard-products",
    ),

    # =====================================================
    # DASHBOARD PRODUCT SEARCH
    # =====================================================

    path(
        "products/product/<str:query>/",
        ProductSearchView.as_view(),
        name="dashboard-product-search",
    ),
]