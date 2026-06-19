from rest_framework import serializers

from .models import (
    Brand,
    ParentCategory,
    ChildCategory,
    ProductImage,
    ProductTag,
    ProductVariant,
    Product,
    CartItem,
    WishlistItem,
)


# -------------------- BASIC SERIALIZERS -------------------- #
class CategorySerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(
        source="sub_category.parent_category.name",
        read_only=True,
    )
    parent_slug = serializers.CharField(
        source="sub_category.parent_category.slug",
        read_only=True,
    )
    sub_name = serializers.CharField(
        source="sub_category.name",
        read_only=True,
    )
    sub_slug = serializers.CharField(
        source="sub_category.slug",
        read_only=True,
    )

    class Meta:
        model = ChildCategory
        fields = [
            "id",
            "name",
            "slug",
            "parent_name",
            "parent_slug",
            "sub_name",
            "sub_slug",
            "image",
            "is_active",
            "sort_order",
        ]


# -------------------- MEGA MENU SERIALIZER -------------------- #
class CategoryMenuSerializer(serializers.ModelSerializer):
    sections = serializers.SerializerMethodField()

    class Meta:
        model = ParentCategory
        fields = ["id", "name", "slug", "sections"]

    def get_sections(self, obj):
        sub_categories = obj.sub_categories.filter(
            is_active=True
        ).order_by("sort_order", "name")

        return [
            {
                "id": sub.id,
                "name": sub.name,
                "slug": sub.slug,
                "items": [
                    {
                        "id": child.id,
                        "name": child.name,
                        "slug": child.slug,
                    }
                    for child in sub.child_categories.filter(
                        is_active=True
                    ).order_by("sort_order", "name")
                ],
            }
            for sub in sub_categories
        ]


# -------------------- BRAND -------------------- #
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = [
            "id",
            "name",
            "slug",
            "logo",
            "description",
            "is_active",
        ]


# -------------------- PRODUCT IMAGE -------------------- #
class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = [
            "id",
            "image",
            "image_url",
            "alt_text",
            "is_primary",
            "sort_order",
        ]

    def get_image_url(self, obj):
        if not obj.image:
            return None

        request = self.context.get("request")
        url = obj.image.url

        return request.build_absolute_uri(url) if request else url


# -------------------- PRODUCT VARIANT -------------------- #
class ProductVariantSerializer(serializers.ModelSerializer):
    available_stock = serializers.ReadOnlyField()

    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "color",
            "size",
            "variant_sku",
            "stock",
            "reserved_stock",
            "available_stock",
            "is_active",
        ]


# -------------------- PRODUCT TAG -------------------- #
class ProductTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTag
        fields = [
            "id",
            "name",
            "slug",
        ]


# -------------------- SHARED HELPERS -------------------- #
class ProductCategoryMixin:
    def get_category_name(self, obj):
        if obj.child_category:
            return obj.child_category.name
        if obj.sub_category:
            return obj.sub_category.name
        if obj.parent_category:
            return obj.parent_category.name
        return None

    def get_category_slug(self, obj):
        if obj.child_category:
            return obj.child_category.slug
        if obj.sub_category:
            return obj.sub_category.slug
        if obj.parent_category:
            return obj.parent_category.slug
        return None


# -------------------- PRODUCT LIST -------------------- #
class ProductListSerializer(ProductCategoryMixin, serializers.ModelSerializer):
    brand = serializers.CharField(source="brand.name", read_only=True)
    brand_slug = serializers.CharField(source="brand.slug", read_only=True)

    category_name = serializers.SerializerMethodField()
    category_slug = serializers.SerializerMethodField()

    discount_percent = serializers.ReadOnlyField()
    primary_image = serializers.SerializerMethodField()
    hover_image = serializers.SerializerMethodField()
    available_sizes = serializers.SerializerMethodField()
    available_colors = serializers.SerializerMethodField()
    in_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "sku",
            "brand",
            "brand_slug",
            "category_name",
            "category_slug",
            "gender",
            "occasion",
            "mrp",
            "selling_price",
            "discount_percent",
            "average_rating",
            "review_count",
            "primary_image",
            "hover_image",
            "available_sizes",
            "available_colors",
            "in_stock",
            "is_featured",
            "is_new_arrival",
            "is_best_seller",
        ]

    def _absolute_image_url(self, image_obj):
        if not image_obj or not image_obj.image:
            return None

        request = self.context.get("request")
        url = image_obj.image.url

        return request.build_absolute_uri(url) if request else url

    def get_primary_image(self, obj):
        image = obj.images.filter(is_primary=True).first() or obj.images.first()
        return self._absolute_image_url(image)

    def get_hover_image(self, obj):
        images = list(obj.images.all()[:2])
        image = images[1] if len(images) > 1 else None
        return self._absolute_image_url(image)

    def get_available_sizes(self, obj):
        return list(
            obj.variants.filter(
                is_active=True,
                stock__gt=0,
            )
            .values_list("size", flat=True)
            .distinct()
        )

    def get_available_colors(self, obj):
        return list(
            obj.variants.filter(
                is_active=True,
                stock__gt=0,
            )
            .values_list("color", flat=True)
            .distinct()
        )


# -------------------- PRODUCT DETAIL -------------------- #
class ProductDetailSerializer(ProductCategoryMixin, serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)
    tags = ProductTagSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)

    category_name = serializers.SerializerMethodField()
    category_slug = serializers.SerializerMethodField()

    discount_percent = serializers.ReadOnlyField()
    in_stock = serializers.ReadOnlyField()
    total_stock = serializers.ReadOnlyField()

    review_count = serializers.SerializerMethodField()

    related_products = serializers.SerializerMethodField()

    def get_review_count(self, obj):
        return 0

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "sku",
            "short_description",
            "description",
            "brand",
            "category_name",
            "category_slug",
            "tags",
            "gender",
            "occasion",
            "mrp",
            "selling_price",
            "discount_percent",
            "average_rating",
            "review_count",
            "in_stock",
            "total_stock",
            "is_featured",
            "is_new_arrival",
            "is_best_seller",
            "is_returnable",
            "is_exchangeable",
            "is_cod_available",
            "meta_title",
            "meta_description",
            "images",
            "variants",
            "related_products",
            "created_at",
            "updated_at",
        ]

    def get_related_products(self, obj):
        queryset = Product.objects.filter(
            is_active=True
        ).exclude(
            id=obj.id
        )

        if obj.child_category:
            queryset = queryset.filter(
                child_category=obj.child_category
            )
        else:
            return []

        queryset = queryset.prefetch_related(
            "images",
            "variants",
        ).select_related(
            "brand",
            "child_category",
        )[:8]

        return ProductListSerializer(
            queryset,
            many=True,
            context=self.context,
        ).data


# -------------------- PRODUCT CREATE / UPDATE -------------------- #
class ProductWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "short_description",
            "description",
            "brand",
            "parent_category",
            "sub_category",
            "child_category",
            "tags",
            "gender",
            "occasion",
            "mrp",
            "selling_price",
            "average_rating",
            "review_count",
            "is_active",
            "is_featured",
            "is_new_arrival",
            "is_best_seller",
            "is_returnable",
            "is_exchangeable",
            "is_cod_available",
            "meta_title",
            "meta_description",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        mrp = attrs.get("mrp", getattr(self.instance, "mrp", None))
        selling_price = attrs.get(
            "selling_price",
            getattr(self.instance, "selling_price", None),
        )

        parent_category = attrs.get(
            "parent_category",
            getattr(self.instance, "parent_category", None),
        )
        sub_category = attrs.get(
            "sub_category",
            getattr(self.instance, "sub_category", None),
        )
        child_category = attrs.get(
            "child_category",
            getattr(self.instance, "child_category", None),
        )

        if (
            sub_category
            and parent_category
            and sub_category.parent_category_id != parent_category.id
        ):
            raise serializers.ValidationError({
                "sub_category": "Selected sub-category does not belong to the selected parent category."
            })

        if (
            child_category
            and sub_category
            and child_category.sub_category_id != sub_category.id
        ):
            raise serializers.ValidationError({
                "child_category": "Selected child category does not belong to the selected sub-category."
            })

        if (
            child_category
            and parent_category
            and child_category.sub_category.parent_category_id != parent_category.id
        ):
            raise serializers.ValidationError({
                "child_category": "Selected child category does not belong to the selected parent category."
            })

        if mrp is not None and selling_price is not None and selling_price > mrp:
            raise serializers.ValidationError({
                "selling_price": "Selling price cannot be greater than MRP."
            })

        average_rating = attrs.get(
            "average_rating",
            getattr(self.instance, "average_rating", 0),
        )

        if average_rating is not None and (average_rating < 0 or average_rating > 5):
            raise serializers.ValidationError({
                "average_rating": "Average rating must be between 0 and 5."
            })

        return attrs


# -------------------- CART -------------------- #
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    variant = ProductVariantSerializer(read_only=True)

    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True),
        source="product",
        write_only=True,
    )
    variant_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.filter(is_active=True),
        source="variant",
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "product_id",
            "variant",
            "variant_id",
            "qty",
            "created_at",
        ]
        read_only_fields = ["id", "product", "variant", "created_at"]

    def validate_qty(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value

    def validate(self, attrs):
        product = attrs.get("product", getattr(self.instance, "product", None))
        variant = attrs.get("variant", getattr(self.instance, "variant", None))
        qty = attrs.get("qty", getattr(self.instance, "qty", 1))

        if variant:
            if variant.product_id != product.id:
                raise serializers.ValidationError({
                    "variant_id": "Selected variant does not belong to this product."
                })

            if not variant.is_active:
                raise serializers.ValidationError({
                    "variant_id": "Selected variant is not active."
                })

            if variant.available_stock < qty:
                raise serializers.ValidationError({
                    "qty": "Requested quantity is not available for this variant."
                })

        else:
            if not product.in_stock:
                raise serializers.ValidationError({
                    "product_id": "This product is currently out of stock."
                })

        return attrs


# -------------------- WISHLIST -------------------- #
class WishlistItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True),
        source="product",
        write_only=True,
    )

    class Meta:
        model = WishlistItem
        fields = [
            "id",
            "product",
            "product_id",
            "created_at",
        ]
        read_only_fields = ["id", "product", "created_at"]