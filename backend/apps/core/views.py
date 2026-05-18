from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from apps.products.models import Product
from vastrika_backend.admin_site import admin_site


class AdminContextMixin:
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
    template_name = "admin/products/change_list.html"
    context_object_name = "products"
    paginate_by = 20

    # QUERYSET
    def get_queryset(self):
        return (
            Product.objects
            .select_related("category", "brand")
            .prefetch_related("tags")
            .order_by("-created_at", "-id")
        )

    # CONTEXT
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            self.get_admin_context()
        )
        return context