# =========================================================
# backend/apps/core/views.py
# =========================================================

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from apps.products.models import Product
from vastrika_backend.admin_site import admin_site


class AdminContextMixin:
    """
    Shared admin context for custom dashboard views.
    """

    @property
    def model_meta(self):
        return self.model._meta

    def get_admin_context(self):
        return {
            **admin_site.each_context(self.request),
            "opts": self.model_meta,
            "app_label": self.model_meta.app_label,
        }


@method_decorator(staff_member_required, name="dispatch")
class DashboardProductListView(AdminContextMixin, ListView):

    model = Product

    template_name = "admin/products/dashboard_product_list.html"

    context_object_name = "products"

    paginate_by = 20

    # =====================================================
    # CLEAN SEARCH URL REDIRECT
    # =====================================================

    def get(self, request, *args, **kwargs):

        query = request.GET.get("q", "").strip()

        if query:
            return redirect(
                f"/dashboard/products/product/{query}/"
            )

        return super().get(request, *args, **kwargs)

    # =====================================================
    # QUERYSET
    # =====================================================

    def get_queryset(self):
        return (
            Product.objects
            .select_related("category", "brand")
            .prefetch_related("tags")
            .order_by("-created_at", "-id")
        )

    # =====================================================
    # CONTEXT
    # =====================================================

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context.update(
            self.get_admin_context()
        )

        return context


@method_decorator(staff_member_required, name="dispatch")
class ProductSearchView(AdminContextMixin, ListView):

    model = Product

    template_name = "admin/products/dashboard_product_list.html"

    context_object_name = "products"

    paginate_by = 20

    # =====================================================
    # SEARCH QUERYSET
    # =====================================================

    def get_queryset(self):

        query = self.kwargs.get(
            "query",
            "",
        ).strip()

        if not query:
            return Product.objects.none()

        return (
            Product.objects
            .select_related("category", "brand")
            .prefetch_related("tags")
            .filter(name__icontains=query)
            .order_by("-created_at", "-id")
        )

    # =====================================================
    # CONTEXT
    # =====================================================

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context.update(
            self.get_admin_context()
        )

        context["search_query"] = self.kwargs.get(
            "query",
            "",
        )

        return context