from __future__ import annotations

from django.urls import (
    path,
)

from apps.core.views import (
    DashboardProductListView,
)


# APP CONFIGURATION
app_name = "core"


# =========================================================
# URL PATTERNS
# =========================================================

urlpatterns = [

    # DASHBOARD API
    path(
        "dashboard/products/",
        DashboardProductListView.as_view(),
        name="dashboard_products",
    ),
]