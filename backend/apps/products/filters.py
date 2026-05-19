from __future__ import annotations

import django_filters

from django.db.models import (
    F,
    Q,
    QuerySet,
)

from apps.products.models import (
    Product,
)


# =========================================================
# PRODUCT FILTER
# =========================================================
class ProductFilter(
    django_filters.FilterSet,
):

    # SEARCH
    search = django_filters.CharFilter(
        method="filter_search",
    )

    # CATEGORY FILTERS
    parent_category = (
        django_filters.NumberFilter(
            field_name="parent_category_id",
        )
    )

    sub_category = (
        django_filters.NumberFilter(
            field_name="sub_category_id",
        )
    )

    child_category = (
        django_filters.NumberFilter(
            field_name="child_category_id",
        )
    )

    # BRAND
    brand = django_filters.NumberFilter(
        field_name="brand_id",
    )

    # PRICE FILTERS
    min_price = (
        django_filters.NumberFilter(
            field_name="selling_price",
            lookup_expr="gte",
        )
    )

    max_price = (
        django_filters.NumberFilter(
            field_name="selling_price",
            lookup_expr="lte",
        )
    )

    # PRODUCT FLAGS
    is_featured = (
        django_filters.BooleanFilter()
    )

    is_new_arrival = (
        django_filters.BooleanFilter()
    )

    is_best_seller = (
        django_filters.BooleanFilter()
    )

    is_active = (
        django_filters.BooleanFilter()
    )

    # STOCK FILTER
    in_stock = (
        django_filters.BooleanFilter(
            method="filter_in_stock",
        )
    )

    # DISCOUNT FILTER
    has_discount = (
        django_filters.BooleanFilter(
            method="filter_discount",
        )
    )

    # GENDER FILTER
    gender = (
        django_filters.CharFilter(
            lookup_expr="iexact",
        )
    )

    # TAG FILTER
    tag = django_filters.CharFilter(
        field_name="tags__slug",
        lookup_expr="iexact",
    )

    # ORDERING
    ordering = (
        django_filters.OrderingFilter(
            fields=(
                (
                    "selling_price",
                    "price",
                ),
                (
                    "created_at",
                    "newest",
                ),
                (
                    "name",
                    "name",
                ),
            )
        )
    )

    # META CONFIGURATION
    class Meta:
        model = Product

        fields = (
            "brand",
            "parent_category",
            "sub_category",
            "child_category",
            "gender",
            "is_active",
            "is_featured",
            "is_new_arrival",
            "is_best_seller",
        )

    # SEARCH FILTER
    def filter_search(
        self,
        queryset: QuerySet,
        name: str,
        value: str,
    ) -> QuerySet:
        if not value:
            return queryset

        return (
            queryset.filter(
                Q(
                    name__icontains=value
                )
                | Q(
                    sku__icontains=value
                )
                | Q(
                    slug__icontains=value
                )
                | Q(
                    short_description__icontains=value
                )
                | Q(
                    description__icontains=value
                )
                | Q(
                    brand__name__icontains=value
                )
            )
            .distinct()
        )

    # STOCK FILTER
    def filter_in_stock(
        self,
        queryset: QuerySet,
        name: str,
        value: bool,
    ) -> QuerySet:
        if value:
            return (
                queryset.filter(
                    variants__stock__gt=0,
                )
                .distinct()
            )

        return queryset

    # DISCOUNT FILTER
    def filter_discount(
        self,
        queryset: QuerySet,
        name: str,
        value: bool,
    ) -> QuerySet:
        if value:
            return queryset.filter(
                selling_price__isnull=False,
                mrp__isnull=False,
                selling_price__lt=F(
                    "mrp"
                ),
            )

        return queryset