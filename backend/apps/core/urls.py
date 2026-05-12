# =========================================================
# backend/apps/core/urls.py
# =========================================================

from django.urls import path

from .views import (
    DashboardProductListView,
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
]