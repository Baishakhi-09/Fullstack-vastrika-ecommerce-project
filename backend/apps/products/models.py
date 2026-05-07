import uuid
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q, Sum
from django.utils.text import slugify


# -------------------- ABSTRACT BASE MODEL -------------------- #
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# -------------------- CATEGORY -------------------- #
class ParentCategory(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    image = models.ImageField(upload_to="categories/parent/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "products_parent_category"
        verbose_name = "Parent Category"
        verbose_name_plural = "Parent Categories"
        ordering = ["sort_order", "name"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or "parent-category"
            slug = base_slug
            counter = 1

            while ParentCategory.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)


class SubCategory(TimeStampedModel):
    parent_category = models.ForeignKey(
        ParentCategory,
        on_delete=models.CASCADE,
        related_name="sub_categories",
    )
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, blank=True)
    image = models.ImageField(upload_to="categories/sub/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "products_sub_category"
        verbose_name = "Sub Category"
        verbose_name_plural = "Sub Categories"
        ordering = ["parent_category__name", "sort_order", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["parent_category", "name"],
                name="unique_sub_category_per_parent",
            ),
        ]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["parent_category"]),
        ]

    def __str__(self):
        return f"{self.parent_category.name} → {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or "sub-category"
            slug = base_slug
            counter = 1

            while SubCategory.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)


class ChildCategory(TimeStampedModel):
    sub_category = models.ForeignKey(
        SubCategory,
        on_delete=models.CASCADE,
        related_name="child_categories",
    )
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, blank=True)
    image = models.ImageField(upload_to="categories/child/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "products_child_category"
        verbose_name = "Child Category"
        verbose_name_plural = "Child Categories"
        ordering = [
            "sub_category__parent_category__name",
            "sub_category__name",
            "sort_order",
            "name",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["sub_category", "name"],
                name="unique_child_category_per_sub_category",
            ),
        ]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["sub_category"]),
        ]

    def __str__(self):
        return (
            f"{self.sub_category.parent_category.name} → "
            f"{self.sub_category.name} → {self.name}"
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or "child-category"
            slug = base_slug
            counter = 1

            while ChildCategory.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)


# -------------------- BRAND -------------------- #
class Brand(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    logo = models.ImageField(upload_to="brands/", blank=True, null=True)
    description = models.TextField(
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "products_brand"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or "brand"
            slug = base_slug
            counter = 1

            while Brand.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)


# -------------------- PRODUCT TAG -------------------- #
class ProductTag(TimeStampedModel):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=80, unique=True, blank=True)

    class Meta:
        db_table = "products_tag"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or "tag"
            slug = base_slug
            counter = 1

            while ProductTag.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)


# -------------------- PRODUCT -------------------- #
class Product(TimeStampedModel):
    GENDER_CHOICES = (
        ("men", "Men"),
        ("women", "Women"),
        ("kids", "Kids"),
        ("unisex", "Unisex"),
    )

    OCCASION_CHOICES = (
        ("casual", "Casual"),
        ("formal", "Formal"),
        ("party", "Party"),
        ("sports", "Sports"),
        ("festive", "Festive"),
        ("ethnic", "Ethnic"),
        ("lounge", "Lounge"),
    )

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    sku = models.CharField(max_length=80, unique=True, blank=True)

    short_description = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)

    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )

    parent_category = models.ForeignKey(
        ParentCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    sub_category = models.ForeignKey(
        SubCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    child_category = models.ForeignKey(
        ChildCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )

    tags = models.ManyToManyField(ProductTag, blank=True, related_name="products")

    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default="unisex")
    occasion = models.CharField(max_length=20, choices=OCCASION_CHOICES, blank=True)

    mrp = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    review_count = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)

    is_returnable = models.BooleanField(default=True)
    is_exchangeable = models.BooleanField(default=True)
    is_cod_available = models.BooleanField(default=True)

    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.CharField(max_length=500, blank=True)

    class Meta:
        db_table = "products_product"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["sku"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["is_featured"]),
            models.Index(fields=["is_new_arrival"]),
            models.Index(fields=["is_best_seller"]),
            models.Index(fields=["gender"]),
            models.Index(fields=["parent_category"]),
            models.Index(fields=["sub_category"]),
            models.Index(fields=["child_category"]),
            models.Index(fields=["brand"]),
            models.Index(fields=["selling_price"]),
            models.Index(fields=["created_at"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(selling_price__gte=0),
                name="products_selling_price_gte_0",
            ),
            models.CheckConstraint(
                check=Q(mrp__gte=0),
                name="products_mrp_gte_0",
            ),
            models.CheckConstraint(
                check=Q(selling_price__lte=F("mrp")),
                name="products_selling_price_lte_mrp",
            ),
            models.CheckConstraint(
                check=Q(average_rating__gte=0) & Q(average_rating__lte=5),
                name="products_avg_rating_between_0_5",
            ),
        ]

    def __str__(self):
        return self.name

    @property
    def discount_percent(self):
        if self.mrp and self.mrp > 0 and self.selling_price is not None:
            discount = ((self.mrp - self.selling_price) / self.mrp) * 100
            return max(0, round(discount))
        return 0

    @property
    def in_stock(self):
        return self.variants.filter(is_active=True, stock__gt=0).exists()

    @property
    def total_stock(self):
        return (
            self.variants.filter(is_active=True).aggregate(total=Sum("stock"))["total"]
            or 0
        )

    def clean(self):
        if self.sub_category and self.parent_category:
            if self.sub_category.parent_category_id != self.parent_category_id:
                raise ValidationError({
                    "sub_category": "Selected sub-category does not belong to the selected parent category."
                })

        if self.child_category and self.sub_category:
            if self.child_category.sub_category_id != self.sub_category_id:
                raise ValidationError({
                    "child_category": "Selected child category does not belong to the selected sub-category."
                })

        if self.child_category and self.parent_category:
            if self.child_category.sub_category.parent_category_id != self.parent_category_id:
                raise ValidationError({
                    "child_category": "Selected child category does not belong to the selected parent category."
                })

        if self.selling_price > self.mrp:
            raise ValidationError({
                "selling_price": "Selling price cannot be greater than MRP."
            })

        if self.average_rating < 0 or self.average_rating > 5:
            raise ValidationError({
                "average_rating": "Average rating must be between 0 and 5."
            })

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = f"SKU-{uuid.uuid4().hex[:10].upper()}"

        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.sku}") or f"product-{self.sku.lower()}"
            slug = base_slug
            counter = 1

            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        self.full_clean()
        super().save(*args, **kwargs)


# -------------------- PRODUCT IMAGE -------------------- #
class ProductImage(TimeStampedModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to="products/")
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "products_product_image"
        ordering = ["sort_order", "id"]
        indexes = [
            models.Index(fields=["product"]),
            models.Index(fields=["is_primary"]),
            models.Index(fields=["sort_order"]),
        ]

    def __str__(self):
        return f"{self.product.name} Image"

    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product
            ).exclude(pk=self.pk).update(is_primary=False)

        super().save(*args, **kwargs)


# -------------------- PRODUCT VARIANT -------------------- #
class ProductVariant(TimeStampedModel):
    SIZE_CHOICES = (
        ("XS", "XS"),
        ("S", "S"),
        ("M", "M"),
        ("L", "L"),
        ("XL", "XL"),
        ("XXL", "XXL"),
        ("FREE", "Free Size"),
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants",
    )

    color = models.CharField(max_length=50)
    size = models.CharField(max_length=20, choices=SIZE_CHOICES, default="M")
    variant_sku = models.CharField(max_length=80, unique=True, blank=True)

    stock = models.PositiveIntegerField(default=0)
    reserved_stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "products_product_variant"
        ordering = ["product", "color", "size"]
        indexes = [
            models.Index(fields=["product"]),
            models.Index(fields=["color"]),
            models.Index(fields=["size"]),
            models.Index(fields=["variant_sku"]),
            models.Index(fields=["stock"]),
            models.Index(fields=["is_active"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["product", "color", "size"],
                name="unique_product_color_size",
            ),
            models.CheckConstraint(
                check=Q(reserved_stock__lte=F("stock")),
                name="reserved_stock_lte_stock",
            ),
        ]

    def __str__(self):
        return f"{self.product.name} | {self.color} | {self.size}"

    @property
    def available_stock(self):
        return max(self.stock - self.reserved_stock, 0)

    def clean(self):
        if self.reserved_stock > self.stock:
            raise ValidationError({
                "reserved_stock": "Reserved stock cannot be greater than stock."
            })

    def save(self, *args, **kwargs):
        if not self.variant_sku:
            self.variant_sku = f"VAR-{uuid.uuid4().hex[:10].upper()}"

        self.full_clean()
        super().save(*args, **kwargs)


# -------------------- WAREHOUSE -------------------- #
class Warehouse(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "products_warehouse"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.name


# -------------------- STOCK -------------------- #
class Stock(TimeStampedModel):
    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="stock_records",
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="stock_records",
        null=True,
        blank=True,
    )
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "products_stock"
        ordering = ["product_variant"]
        constraints = [
            models.UniqueConstraint(
                fields=["product_variant", "warehouse"],
                name="unique_variant_warehouse_stock",
            ),
        ]
        indexes = [
            models.Index(fields=["product_variant"]),
            models.Index(fields=["warehouse"]),
        ]

    def __str__(self):
        return f"{self.product_variant} - {self.quantity}"


# -------------------- CART -------------------- #
class CartItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart_items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cart_products",
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cart_items",
    )
    qty = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "products_cart_item"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product", "variant"],
                name="unique_cart_user_product_variant",
            ),
            models.CheckConstraint(
                check=Q(qty__gte=1),
                name="cart_qty_gte_1",
            ),
        ]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["product"]),
            models.Index(fields=["variant"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.product.name} ({self.qty})"


# -------------------- WISHLIST -------------------- #
class WishlistItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist_items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="wishlist_products",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "products_wishlist_item"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_wishlist_user_product",
            )
        ]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["product"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.product.name}"