import csv
from decimal import Decimal

from openpyxl import Workbook

from django.views.generic import DetailView

from django.contrib.admin.views.decorators import (
    staff_member_required,
)

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from django.db.models import Max, Min, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from .models import (
    Brand,
    CartItem,
    ParentCategory,
    ChildCategory,
    Product,
    ProductTag,
    ProductVariant,
    WishlistItem,
)
from .serializers import (
    CategoryMenuSerializer,
    CategorySerializer,
    BrandSerializer,
    CartItemSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    ProductTagSerializer,
    WishlistItemSerializer,
)
from .pagination import ProductPagination


@staff_member_required
def export_products_csv(request):
    response = HttpResponse(
        content_type="text/csv; charset=utf-8"
    )

    response["Content-Disposition"] = (
        'attachment; filename="products.csv"'
    )

    response.write("\ufeff")

    writer = csv.writer(response)

    writer.writerow([
        "ID",
        "Name",
        "Brand",
        "Parent Category",
        "Sub Category",
        "Child Category",
        "Selling Price",
        "MRP",
        "Stock",
        "Status",
    ])

    products = (
        Product.objects.select_related(
            "brand",
            "parent_category",
            "sub_category",
            "child_category",
        )
        .prefetch_related("variants")
        .order_by("-created_at")
    )

    for product in products:
        total_stock = sum(
            variant.stock
            for variant in product.variants.all()
        )

        writer.writerow([
            product.id,
            product.name,
            getattr(product.brand, "name", "-"),
            getattr(product.parent_category, "name", "-"),
            getattr(product.sub_category, "name", "-"),
            getattr(product.child_category, "name", "-"),
            product.selling_price,
            product.mrp,
            total_stock,
            "Active" if product.is_active else "Inactive",
        ])

    return response


@staff_member_required
def export_products_excel(request):
    workbook = Workbook()

    worksheet = workbook.active
    worksheet.title = "Products"

    headers = [
        "ID",
        "Name",
        "Brand",
        "Parent Category",
        "Sub Category",
        "Child Category",
        "Selling Price",
        "MRP",
        "Stock",
        "Status",
    ]

    worksheet.append(headers)

    products = (
        Product.objects.select_related(
            "brand",
            "parent_category",
            "sub_category",
            "child_category",
        )
        .prefetch_related("variants")
        .order_by("-created_at")
    )

    for product in products:

        total_stock = sum(
            variant.stock
            for variant in product.variants.all()
        )

        worksheet.append([
            product.id,
            product.name,
            getattr(product.brand, "name", "-"),
            getattr(product.parent_category, "name", "-"),
            getattr(product.sub_category, "name", "-"),
            getattr(product.child_category, "name", "-"),
            product.selling_price,
            product.mrp,
            total_stock,
            "Active" if product.is_active else "Inactive",
        ])

    response = HttpResponse(
        content_type=(
            "application/vnd.openxmlformats-officedocument"
            ".spreadsheetml.sheet"
        )
    )

    response["Content-Disposition"] = (
        'attachment; filename="products.xlsx"'
    )

    workbook.save(response)

    return response


@staff_member_required
def export_products_pdf(request):

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        'attachment; filename="products.pdf"'
    )

    document = SimpleDocTemplate(
        response,
        pagesize=letter,
    )

    elements = []

    data = [[
        "ID",
        "Name",
        "Brand",
        "Price",
        "Stock",
        "Status",
    ]]

    products = (
        Product.objects.select_related(
            "brand",
            "parent_category",
            "sub_category",
            "child_category",
        )
        .prefetch_related("variants")
        .order_by("-created_at")
    )

    for product in products:

        total_stock = sum(
            variant.stock
            for variant in product.variants.all()
        )

        data.append([
            str(product.id),
            product.name,
            getattr(product.brand, "name", "-"),
            str(product.selling_price),
            str(total_stock),
            (
                "Active"
                if product.is_active
                else "Inactive"
            ),
        ])

    table = Table(
        data,
        colWidths=[40, 120, 80, 70, 60, 70],
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.black),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("GRID", (0, 0), (-1, -1), 1, colors.grey),

        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),

        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 12))

    document.build(elements)

    return response


# -------------------- PRODUCT LIST / PLP -------------------- #
class ProductListAPIView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    pagination_class = ProductPagination
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = (
            Product.objects.filter(is_active=True)
            .select_related(
                "brand",
                "parent_category",
                "sub_category",
                "child_category",
            )
            .prefetch_related(
                "images",
                "variants",
                "tags",
            )
            .distinct()
        )

        params = self.request.query_params

        search = params.get("search") or params.get("q")
        category = params.get("category")
        parent = params.get("parent")
        sub = params.get("sub")
        child = params.get("child")
        brand = params.get("brand")
        gender = params.get("gender")
        occasion = params.get("occasion")
        color = params.get("color")
        size = params.get("size")
        min_price = params.get("min_price")
        max_price = params.get("max_price")
        min_rating = params.get("min_rating")
        in_stock = params.get("in_stock")
        is_featured = params.get("featured")
        is_new_arrival = params.get("new_arrival")
        is_best_seller = params.get("best_seller")
        tag = params.get("tag")
        sort = params.get("sort")

        def to_bool(value):
            return (
                str(value).strip().lower()
                in {"true", "1", "yes"}
            )

        def is_number(value):
            try:
                Decimal(str(value))
                return True
            except Exception:
                return False

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(short_description__icontains=search)
                | Q(description__icontains=search)
                | Q(sku__icontains=search)
                | Q(brand__name__icontains=search)
                | Q(parent_category__name__icontains=search)
                | Q(sub_category__name__icontains=search)
                | Q(child_category__name__icontains=search)
                | Q(tags__name__icontains=search)
            )

        if category:
            queryset = queryset.filter(
                Q(parent_category__slug__iexact=category)
                | Q(sub_category__slug__iexact=category)
                | Q(child_category__slug__iexact=category)
            )

        if parent:
            queryset = queryset.filter(parent_category__slug__iexact=parent)

        if sub:
            queryset = queryset.filter(sub_category__slug__iexact=sub)

        if child:
            queryset = queryset.filter(child_category__slug__iexact=child)

        if brand:
            queryset = queryset.filter(brand__slug__iexact=brand)

        if gender:
            queryset = queryset.filter(gender__iexact=gender)

        if occasion:
            queryset = queryset.filter(occasion__iexact=occasion)

        if color:
            queryset = queryset.filter(
                variants__is_active=True,
                variants__stock__gt=0,
                variants__color__iexact=color,
            )

        if size:
            queryset = queryset.filter(
                variants__is_active=True,
                variants__stock__gt=0,
                variants__size__iexact=size,
            )

        if min_price and is_number(min_price):
            queryset = queryset.filter(selling_price__gte=Decimal(str(min_price)))

        if max_price and is_number(max_price):
            queryset = queryset.filter(selling_price__lte=Decimal(str(max_price)))

        if min_rating and is_number(min_rating):
            queryset = queryset.filter(average_rating__gte=Decimal(str(min_rating)))

        if to_bool(in_stock):
            queryset = queryset.filter(
                variants__is_active=True,
                variants__stock__gt=0,
            )

        if to_bool(is_featured):
            queryset = queryset.filter(is_featured=True)

        if to_bool(is_new_arrival):
            queryset = queryset.filter(is_new_arrival=True)

        if to_bool(is_best_seller):
            queryset = queryset.filter(is_best_seller=True)

        if tag:
            queryset = queryset.filter(
                Q(tags__slug__iexact=tag)
                | Q(tags__name__iexact=tag)
            )

        sort_options = {
            "price_low_to_high": ("selling_price", "-id"),
            "price_high_to_low": ("-selling_price", "-id"),
            "newest": ("-created_at",),
            "oldest": ("created_at",),
            "rating": ("-average_rating", "-review_count"),
            "discount": ("-mrp", "selling_price"),
            "popular": ("-review_count",),
            "name_asc": ("name",),
            "name_desc": ("-name",),
        }

        return queryset.distinct().order_by(*sort_options.get(sort, ("-created_at",)))


# -------------------- PRODUCT DETAIL -------------------- #
class ProductDetailAPIView(generics.RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        return (
            Product.objects.filter(is_active=True)
            .select_related(
                "brand",
                "parent_category",
                "sub_category",
                "child_category",
            )
            .prefetch_related(
                "images",
                "variants",
                "tags",
            )
        )


# -------------------- FILTER META -------------------- #
class ProductFilterMetaAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        products = Product.objects.filter(is_active=True)

        price_range = products.aggregate(
            min_price=Min("selling_price"),
            max_price=Max("selling_price"),
        )

        categories = CategorySerializer(
            ChildCategory.objects.filter(
                is_active=True,
                sub_category__is_active=True,
                sub_category__parent_category__is_active=True,
            )
            .select_related("sub_category", "sub_category__parent_category")
            .order_by("sort_order", "name"),
            many=True,
            context={"request": request},
        ).data

        brands = BrandSerializer(
            Brand.objects.filter(is_active=True).order_by("name"),
            many=True,
            context={"request": request},
        ).data

        tags = ProductTagSerializer(
            ProductTag.objects.all().order_by("name"),
            many=True,
        ).data

        sizes = (
            ProductVariant.objects.filter(
                is_active=True,
                product__is_active=True,
                stock__gt=0,
            )
            .values_list("size", flat=True)
            .distinct()
            .order_by("size")
        )

        colors = (
            ProductVariant.objects.filter(
                is_active=True,
                product__is_active=True,
                stock__gt=0,
            )
            .values_list("color", flat=True)
            .distinct()
            .order_by("color")
        )

        return Response(
            {
                "price_range": price_range,
                "categories": categories,
                "brands": brands,
                "tags": tags,
                "sizes": [size for size in sizes if size],
                "colors": [color for color in colors if color],
                "gender_options": [
                    {"value": value, "label": label}
                    for value, label in Product.GENDER_CHOICES
                ],
                "occasion_options": [
                    {"value": value, "label": label}
                    for value, label in Product.OCCASION_CHOICES
                ],
                "sort_options": [
                    {"value": "newest", "label": "Newest"},
                    {"value": "oldest", "label": "Oldest"},
                    {"value": "price_low_to_high", "label": "Price: Low to High"},
                    {"value": "price_high_to_low", "label": "Price: High to Low"},
                    {"value": "rating", "label": "Top Rated"},
                    {"value": "popular", "label": "Popularity"},
                    {"value": "discount", "label": "Best Discount"},
                    {"value": "name_asc", "label": "Name A-Z"},
                    {"value": "name_desc", "label": "Name Z-A"},
                ],
            },
            status=status.HTTP_200_OK,
        )


# -------------------- MEGA MENU -------------------- #
class MegaMenuView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        parents = (
            ParentCategory.objects.filter(is_active=True)
            .prefetch_related("sub_categories__child_categories")
            .order_by("sort_order", "name")
        )

        serializer = CategoryMenuSerializer(parents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# -------------------- RELATED PRODUCTS -------------------- #
class RelatedProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        slug = self.kwargs.get("slug")

        product = get_object_or_404(
            Product.objects.select_related(
                "parent_category",
                "sub_category",
                "child_category",
            ),
            slug=slug,
            is_active=True,
        )

        queryset = Product.objects.filter(is_active=True).exclude(id=product.id)

        if product.child_category:
            queryset = queryset.filter(child_category=product.child_category)
        elif product.sub_category:
            queryset = queryset.filter(sub_category=product.sub_category)
        elif product.parent_category:
            queryset = queryset.filter(parent_category=product.parent_category)
        else:
            return Product.objects.none()

        return (
            queryset.select_related(
                "brand",
                "parent_category",
                "sub_category",
                "child_category",
            )
            .prefetch_related("images", "variants", "tags")
            .order_by("-created_at")[:8]
        )


# -------------------- CATEGORY LIST -------------------- #
class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = ChildCategory.objects.filter(
            is_active=True,
            sub_category__is_active=True,
            sub_category__parent_category__is_active=True,
        ).select_related("sub_category", "sub_category__parent_category")

        parent = self.request.query_params.get("parent")
        sub = self.request.query_params.get("sub")

        if parent:
            queryset = queryset.filter(
                Q(sub_category__parent_category__slug__iexact=parent)
            )

        if sub:
            queryset = queryset.filter(Q(sub_category__slug__iexact=sub))

        return queryset.order_by("sort_order", "name")


# -------------------- BRAND LIST -------------------- #
class BrandListView(generics.ListAPIView):
    serializer_class = BrandSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Brand.objects.filter(is_active=True).order_by("name")
    
class BrandDetailView(DetailView):
    model = Brand
    template_name = "admin/products/brand-detail.html"
    context_object_name = "brand"
    slug_field = "slug"
    slug_url_kwarg = "slug"


# -------------------- TAG LIST -------------------- #
class ProductTagListView(generics.ListAPIView):
    serializer_class = ProductTagSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return ProductTag.objects.all().order_by("name")


# -------------------- CART LIST / CREATE -------------------- #
class CartItemListCreateView(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            CartItem.objects.filter(user=self.request.user)
            .select_related(
                "product",
                "variant",
                "product__brand",
                "product__parent_category",
                "product__sub_category",
                "product__child_category",
            )
            .prefetch_related(
                "product__images",
                "product__variants",
            )
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        product = serializer.validated_data["product"]
        variant = serializer.validated_data.get("variant")
        qty = serializer.validated_data.get("qty", 1)

        cart_item, created = CartItem.objects.get_or_create(
            user=self.request.user,
            product=product,
            variant=variant,
            defaults={"qty": qty},
        )

        if not created:
            new_qty = cart_item.qty + qty

            if variant and variant.available_stock < new_qty:
                raise serializers.ValidationError({
                    "qty": "Requested quantity exceeds available stock."
                })

            cart_item.qty = new_qty
            cart_item.save(update_fields=["qty"])

        serializer.instance = cart_item


# -------------------- CART UPDATE / DELETE -------------------- #
class CartItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            CartItem.objects.filter(user=self.request.user)
            .select_related(
                "product",
                "variant",
                "product__brand",
                "product__parent_category",
                "product__sub_category",
                "product__child_category",
            )
            .prefetch_related(
                "product__images",
                "product__variants",
            )
        )


# -------------------- CART SUMMARY -------------------- #
class CartSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart_items = (
            CartItem.objects.filter(user=request.user)
            .select_related("product", "variant")
        )

        subtotal = Decimal("0.00")
        total_qty = 0

        for item in cart_items:
            subtotal += Decimal(item.product.selling_price) * item.qty
            total_qty += item.qty

        return Response(
            {
                "total_items": cart_items.count(),
                "total_qty": total_qty,
                "subtotal": subtotal,
            },
            status=status.HTTP_200_OK,
        )


# -------------------- WISHLIST LIST / CREATE -------------------- #
class WishlistItemListCreateView(generics.ListCreateAPIView):
    serializer_class = WishlistItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            WishlistItem.objects.filter(user=self.request.user)
            .select_related(
                "product",
                "product__brand",
                "product__parent_category",
                "product__sub_category",
                "product__child_category",
            )
            .prefetch_related(
                "product__images",
                "product__variants",
            )
            .order_by("-created_at")
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = serializer.validated_data["product"]

        wishlist_item, created = WishlistItem.objects.get_or_create(
            user=request.user,
            product=product,
        )

        output = self.get_serializer(wishlist_item)

        return Response(
            output.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


# -------------------- WISHLIST DELETE -------------------- #
class WishlistItemDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = WishlistItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            WishlistItem.objects.filter(user=self.request.user)
            .select_related("product")
        )


# -------------------- WISHLIST CHECK -------------------- #
class WishlistCheckView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, product_id):
        exists = WishlistItem.objects.filter(
            user=request.user,
            product_id=product_id,
        ).exists()

        return Response(
            {"in_wishlist": exists},
            status=status.HTTP_200_OK,
        )