from datetime import timedelta

from django.contrib.admin import AdminSite
from django.contrib.auth import logout as auth_logout
from django.core.cache import cache
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.timezone import now

from apps.orders.models import Order
from apps.products.models import (
    Brand,
    CartItem,
    ChildCategory,
    ParentCategory,
    Product,
    SubCategory,
    WishlistItem,
)
from apps.site_settings.models import SettingFile, SettingGroup
from apps.site_settings.seed_settings import create_default_settings


class VastrikaAdminSite(AdminSite):
    site_header = "Vastrika Administration"
    site_title = "Vastrika Admin"
    index_title = "E-Commerce Admin Dashboard"
    login_template = "admin/login.html"

    # =========================================================
    # AUTH
    # =========================================================
    def login(self, request, extra_context=None):
        request.GET = request.GET.copy()
        request.GET.pop("next", None)
        return super().login(request, extra_context)

    def logout(self, request, extra_context=None):
        auth_logout(request)
        return redirect(reverse("admin:login", current_app=self.name))

    # =========================================================
    # URLS
    # =========================================================
    def get_urls(self):
        custom_urls = [
            path("", self.admin_view(self.custom_index), name="index",),
            path(
                "search-suggestions/",
                self.admin_view(self.search_suggestions),
                name="search_suggestions",
            ),
            path(
                "settings/<slug:group_key>/",
                self.admin_view(self.settings_group_view),
                name="settings_group",
            ),
        ]

        return custom_urls + super().get_urls()

    # =========================================================
    # DASHBOARD
    # =========================================================
    def custom_index(self, request):
        today = now()
        last_7_days = today - timedelta(days=7)

        cache_key = "vastrika_admin_dashboard_metrics"
        dashboard_data = cache.get(cache_key)

        if dashboard_data is None:
            total_orders = Order.objects.count()
            total_revenue = (
                Order.objects.filter(status__in=["paid", "delivered"])
                .aggregate(total=Sum("total_amount"))
                .get("total")
                or 0
            )

            pending_orders = Order.objects.filter(status="pending").count()
            paid_orders = Order.objects.filter(status="paid").count()
            delivered_orders = Order.objects.filter(status="delivered").count()
            cancelled_orders = Order.objects.filter(status="cancelled").count()

            total_products = Product.objects.count()
            total_brands = Brand.objects.count()
            total_parent_categories = ParentCategory.objects.count()
            total_sub_categories = SubCategory.objects.count()
            total_child_categories = ChildCategory.objects.count()
            total_cart_items = CartItem.objects.count()
            total_wishlist_items = WishlistItem.objects.count()

            daily_orders = list(
                Order.objects.filter(placed_at__gte=last_7_days)
                .annotate(day=TruncDate("placed_at"))
                .values("day")
                .annotate(count=Count("id"))
                .order_by("day")
            )

            sales_labels = [
                item["day"].strftime("%d %b") for item in daily_orders if item["day"]
            ]

            sales_data = [item["count"] for item in daily_orders]

            dashboard_data = {
                "total_orders": total_orders,
                "total_revenue": total_revenue,
                "pending_orders": pending_orders,
                "paid_orders": paid_orders,
                "delivered_orders": delivered_orders,
                "cancelled_orders": cancelled_orders,
                "total_products": total_products,
                "total_brands": total_brands,
                "total_parent_categories": total_parent_categories,
                "total_sub_categories": total_sub_categories,
                "total_child_categories": total_child_categories,
                "total_cart_items": total_cart_items,
                "total_wishlist_items": total_wishlist_items,
                "sales_labels": sales_labels,
                "sales_data": sales_data,
                "category_labels": ["Parent", "Sub", "Child"],
                "category_data": [
                    total_parent_categories,
                    total_sub_categories,
                    total_child_categories,
                ],
            }

            cache.set(cache_key, dashboard_data, 60)

        recent_orders = Order.objects.order_by("-placed_at")[:6]
        recent_products = Product.objects.order_by("-created_at")[:6]

        context = {
            **self.each_context(request),
            # "title": "Dashboard",
            "last_7_days": last_7_days,
            "recent_orders": recent_orders,
            "recent_products": recent_products,
            **dashboard_data,
        }

        return TemplateResponse(
            request,
            "admin/custom_index.html",
            context,
        )

    # =========================================================
    # SETTINGS GROUP PAGE
    # =========================================================
    def settings_group_view(self, request, group_key):
        if not request.user.is_superuser:
            return redirect(reverse("admin:index", current_app=self.name))
        
        create_default_settings()

        group = get_object_or_404(
            SettingGroup.objects.prefetch_related("fields"),
            key=group_key,
            is_active=True,
        )

        fields = group.fields.filter(is_active=True).order_by("order")

        if request.method == "POST":
            self._save_settings_fields(request, fields)
            return redirect(request.path)

        context = {
            **self.each_context(request),
            "title": group.name,
            "group": group,
            "fields": fields,
            "setting_groups": SettingGroup.objects.filter(is_active=True).order_by(
                "sort_order",
                "name",
            ),
        }

        return TemplateResponse(
            request,
            "admin/settings_group.html",
            context,
        )
    
    def _save_settings_fields(self, request, fields):
        for field in fields:
            if field.field_type == "file":
                uploaded_file = request.FILES.get(field.key)

                if uploaded_file:
                    setting_file, _ = SettingFile.objects.get_or_create(field=field)
                    setting_file.file = uploaded_file
                    setting_file.save()

                    field.value = setting_file.file.url
                    field.save(update_fields=["value"])

            elif field.field_type == "toggle":
                field.value = "true" if request.POST.get(field.key) == "true" else "false"
                field.save(update_fields=["value"])

            elif field.field_type == "password":
                value = request.POST.get(field.key, "").strip()

                if value:
                    field.value = value
                    field.save(update_fields=["value"])

            else:
                field.value = request.POST.get(field.key, "")
                field.save(update_fields=["value"])

    # =========================================================
    # GLOBAL SEARCH
    # =========================================================

    def search_suggestions(self, request):
        query = request.GET.get("q", "").strip()
        results = []

        if not query:
            return JsonResponse({"results": results})

        app_list = self.get_app_list(request)

        for app in app_list:
            for model_dict in app.get("models", []):
                model = model_dict.get("model")
                if not model:
                    continue

                model_admin = self._registry.get(model)

                if not model_admin:
                    continue

                search_fields = getattr(model_admin, "search_fields", [])

                if not search_fields:
                    continue

                q_objects = self._build_search_query(search_fields, query)

                if not q_objects:
                    continue

                try:
                    queryset = model.objects.filter(q_objects)[:5]
                except Exception:
                    continue

                for obj in queryset:
                    change_url = self._get_admin_change_url(obj, model)

                    if not change_url:
                        continue

                    results.append(
                        {
                            "title": str(obj),
                            "model": model._meta.verbose_name.title(),
                            "url": change_url,
                        }
                    )
        return JsonResponse({"results": results[:10]})
    
    def _build_search_query(self, search_fields, query):
        q_objects = Q()

        for field in search_fields:
            if field.startswith("@"):
                continue

            if field.startswith("^"):
                field_name = field[1:]
                lookup = f"{field_name}__istartswith"

            elif field.startswith("="):
                field_name = field[1:]
                lookup = f"{field_name}__iexact"

            else:
                field_name = field
                lookup = f"{field_name}__icontains"

            q_objects |= Q(**{lookup: query})

        return q_objects
    
    def _get_admin_change_url(self, obj, model):
        try:
            return reverse(
                f"admin:{model._meta.app_label}_{model._meta.model_name}_change",
                args=[obj.pk],
                current_app=self.name,
            )
        except Exception:
            return None
        
admin_site = VastrikaAdminSite(name="vastrika_admin")