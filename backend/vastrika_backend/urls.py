"""
URL configuration for vastrika_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.views.generic import RedirectView

from apps.accounts.views import AdminPasswordChangeView
from vastrika_backend.admin_site import admin_site

urlpatterns = [

    # =========================================================
    # OLD ADMIN URL REDIRECTS
    # =========================================================

    # Clean Admin Login URL
    path(
        "admin-login/", RedirectView.as_view( url="/dashboard/login/", permanent=False,),
        name="admin_login_redirect",
    ),

    # Old Django Admin Redirect
    path(
        "admin/",
        RedirectView.as_view(
            url="/dashboard/",
            permanent=False,
        ),
    ),

    # =========================================================
    # ADMIN PASSWORD CHANGE
    # =========================================================
    path(
        "dashboard/password_change/",
        AdminPasswordChangeView.as_view(),
        name="admin_password_change",
    ),

    path(
        "dashboard/",
        include("apps.core.urls"),
    ),

    # =========================================================
    # CUSTOM ADMIN DASHBOARD
    # =========================================================
    path("dashboard/", admin_site.urls),

    # =========================================================
    # API ROUTES
    # =========================================================
    path("api/auth/", include("apps.accounts.urls")), # User
    path("api/products/", include("apps.products.urls")), #Products
    path("api/settings/", include("apps.site_settings.urls")),
    path("api/admin/notifications/", include("apps.products.notifications.urls")),
]

# =============================================================
# MEDIA FILES (DEVELOPMENT ONLY)
# =============================================================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)