import uuid
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db.models.functions import Lower
from django.db import models
from django.db.models import F, Q, Sum
from django.utils.text import slugify
from django.urls import reverse


# -------------------- ABSTRACT BASE MODEL -------------------- #
class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            is_deleted=False
        )
    
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created"
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated"
    )

    is_deleted = models.BooleanField(
        default=False
    )

    deleted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True


# -------------------- CATEGORY -------------------- #
class ParentCategory(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("published", "Published"),
        ("archived", "Archived"),
    )

    name = models.CharField(
        max_length=120
    )

    slug = models.SlugField(
        unique=True
    )

    short_description = models.CharField(
        max_length=255,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    icon = models.ImageField(
        upload_to="categories/icons/",
        blank=True,
        null=True
    )

    image = models.ImageField(
        upload_to="categories/images/", 
        blank=True, 
        null=True
    )

    banner = models.ImageField(
        upload_to="categories/banners/",
        blank=True,
        null=True
    )

    brands = models.ManyToManyField(
        "Brand",
        blank=True,
        related_name="parent_categories"
    )

    tags = models.ManyToManyField(
        "ProductTag",
        blank=True,
        related_name="parent_categories"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )

    is_featured = models.BooleanField(
        default=False
    )

    show_in_menu = models.BooleanField(
        default=True
    )

    sort_order = models.PositiveIntegerField(
        default=0
    )

    view_count = models.PositiveIntegerField(
        default=0,
        editable=False
    )

    meta_title = models.CharField(
        max_length=255,
        blank=True
    )

    meta_description = models.TextField(
        blank=True
    )

    seo_keywords = models.CharField(
        max_length=500,
        blank=True
    )

    canonical_url = models.URLField(
        blank=True
    )

    class Meta:
        db_table = "products_parent_category"
        verbose_name = "Parent Category"
        verbose_name_plural = "Parent Categories"
        ordering = ["sort_order", "name"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["is_featured"]),
            models.Index(fields=["show_in_menu"]),
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
    description = models.TextField(
        blank=True,
        null=True
    )

    meta_title = models.CharField(
        max_length=60,
        blank=True
    )

    meta_description = models.TextField(
        blank=True
    )
    
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
    description = models.TextField(
        blank=True,
        null=True
    )

    meta_title = models.CharField(
        max_length=60,
        blank=True
    )

    meta_description = models.TextField(
        blank=True
    )
    
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
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    logo = models.ImageField(upload_to="brands/", blank=True, null=True)
    description = models.TextField(
        blank=True,
        null=True,
    )

    meta_title = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    meta_description = models.TextField(
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "products_brand"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.name
    
    def clean(self):
        existing_brand = Brand.objects.filter(
            name__iexact=self.name
        ).exclude(pk=self.pk)

        if existing_brand.exists():
            raise ValidationError({
                "name": "A brand with this name already exists."
            })

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = (
                slugify(self.name)
                .replace("-", "")
            ) or "brand"
            slug = base_slug
            counter = 1

            while Brand.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}{counter}"
                counter += 1

            self.slug = slug
        
        self.full_clean()

        super().save(*args, **kwargs)


# -------------------- PRODUCT TAG -------------------- #
class ProductTag(TimeStampedModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(
        unique=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("published", "Published"),
        ("archived", "Archived"),
    )

    VISIBILITY_CHOICES = (
        ("public", "Public"),
        ("private", "Private"),
        ("hidden", "Hidden"),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )

    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default="public"
    )

    is_featured = models.BooleanField(
        default=False
    )

    display_priority = models.PositiveIntegerField(
        default=0
    )

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
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("published", "Published"),
        ("archived", "Archived"),
    )

    GST_CHOICES = (
        ("gst_0", "GST 0%"),
        ("gst_5", "GST 5%"),
        ("gst_12", "GST 12%"),
        ("gst_18", "GST 18%"),
        ("gst_28", "GST 28%"),
    )

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

    SHIPPING_CLASS_CHOICES = (
        ("standard", "Standard"),
        ("express", "Express"),
        ("fragile", "Fragile"),
    )

    DELIVERY_TIME_CHOICES = (
        ("1-2_days", "1-2 Days"),
        ("3-5_days", "3-5 Days"),
        ("5-7_days", "5-7 Days"),
    )

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    short_description = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)

    video = models.FileField(
        upload_to="products/videos/",
        blank=True,
        null=True,
        help_text="Upload MP4, WEBM or MOV video."
    )

    brand = models.ForeignKey(
        "products.Brand",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # parent_category = models.ForeignKey(
    #     ParentCategory,
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name="products",
    # )

    # sub_category = models.ForeignKey(
    #     SubCategory,
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name="products",
    # )

    child_category = models.ForeignKey(
        ChildCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )

    tags = models.ManyToManyField(ProductTag, blank=True, related_name="products")

    collection = models.CharField(
        max_length=120,
        blank=True
    )

    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    mrp = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    tax = models.CharField(
        max_length=20,
        choices=GST_CHOICES,
        default="gst_0",
    )

    sku = models.CharField(max_length=80, unique=True, blank=True)

    barcode = models.CharField(
        max_length=120,
        blank=True
    )

    allow_backorders = models.BooleanField(
        default=False
    )

    # stock = models.PositiveIntegerField(
    #     default=0
    # )

    # low_stock_threshold = models.PositiveIntegerField(
    #     default=5
    # )

    shipping_class = models.CharField(
        max_length=50,
        choices=SHIPPING_CLASS_CHOICES,
        default="standard",
    )

    delivery_time = models.CharField(
        max_length=50,
        choices=DELIVERY_TIME_CHOICES,
        default="3-5_days",
    )

    free_shipping = models.BooleanField(
        default=False
    )

    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    length = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    width = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    height = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default="unisex")
    occasion = models.CharField(max_length=20, choices=OCCASION_CHOICES, blank=True)

    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.CharField(
        max_length=500,
        blank=True
    )

    og_image = models.ImageField(
        upload_to="products/seo/",
        blank=True,
        null=True,
    )

    seo_keywords = models.CharField(
        max_length=500,
        blank=True
    )

    search_keywords = models.TextField(
        blank=True
    )

    canonical_url = models.URLField(
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )

    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)

    is_trending = models.BooleanField(
        default=False
    )

    is_hot = models.BooleanField(
        default=False
    )

    is_returnable = models.BooleanField(default=True)
    is_exchangeable = models.BooleanField(default=True)
    is_cod_available = models.BooleanField(default=True)

    class Meta:
        db_table = "products_product"
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["brand"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["sku"]),
            models.Index(fields=["is_featured"]),
            models.Index(fields=["is_new_arrival"]),
            models.Index(fields=["is_best_seller"]),
            models.Index(fields=["gender"]),
            # models.Index(fields=["parent_category"]),
            # models.Index(fields=["sub_category"]),
            models.Index(fields=["child_category"]),
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
    def profit(self):
        return self.selling_price - self.cost_price

    @property
    def final_selling_price(self):
        gst_map = {
            "gst_0": Decimal("0"),
            "gst_5": Decimal("5"),
            "gst_12": Decimal("12"),
            "gst_18": Decimal("18"),
            "gst_28": Decimal("28"),
        }

        gst_percent = gst_map.get(
            self.tax,
            Decimal("0")
        )

        tax_amount = (
            self.selling_price *
            gst_percent /
            Decimal("100")
        )

        return self.selling_price + tax_amount
    
    @property
    def in_stock(self):
        return self.variants.filter(is_active=True, stock__gt=0).exists()
    
    @property
    def total_stock(self):
        return (
            self.variants.filter(is_active=True).aggregate(total=Sum("stock"))["total"]
            or 0
        )
    
    @property
    def primary_image(self):

        return (
            self.images
            .filter(is_primary=True)
            .first()
        )


    @property
    def primary_image_url(self):

        image = self.primary_image

        if image and image.image:
            return image.image.url

        return None
    
    @property
    def stock_status(self):

        if self.total_stock <= 0:
            return "Out of Stock"

        if self.total_stock <= 5:
            return "Low Stock"

        return "In Stock"
    
    def clean(self):
        # if self.sub_category and self.parent_category:
        #     if self.sub_category.parent_category_id != self.parent_category_id:
        #         raise ValidationError({
        #             "sub_category": "Selected sub-category does not belong to the selected parent category."
        #         })
            
        #     if self.child_category and self.sub_category:
        #         if self.child_category.sub_category_id != self.sub_category_id:
        #             raise ValidationError({
        #                 "child_category": "Selected child category does not belong to the selected sub-category."
        #             })

        # if self.child_category and self.parent_category:
        #     if self.child_category.sub_category.parent_category_id != self.parent_category_id:
        #         raise ValidationError({
        #             "child_category": "Selected child category does not belong to the selected parent category."
        #         })

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

    def get_absolute_url(self):
        return reverse(
            "product_detail",
            kwargs={
                "slug": self.slug
            }
        )


# -------------------- PRODUCT IMAGE -------------------- #
class ProductImage(TimeStampedModel):
    IMAGE_TYPE_CHOICES = (
        ("primary", "Primary"),
        ("gallery", "Gallery"),
        ("zoom", "Zoom"),
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
    )

    image = models.ImageField(
        upload_to="products/images/"
    )

    image_type = models.CharField(
        max_length=20,
        choices=IMAGE_TYPE_CHOICES,
        default="gallery",
    )

    alt_text = models.CharField(max_length=255, blank=True,)
    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "products_product_image"
        ordering = ["-is_primary","sort_order", "id",]
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
    # SIZE_CHOICES = (
    #     ("XS", "XS"),
    #     ("S", "S"),
    #     ("M", "M"),
    #     ("L", "L"),
    #     ("XL", "XL"),
    #     ("XXL", "XXL"),
    #     ("FREE", "Free Size"),
    # )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants",
    )

    color = models.CharField(max_length=50)
    size = models.CharField(max_length=20, default="M")
    variant_sku = models.CharField(max_length=80, unique=True, blank=True)

    barcode = models.CharField(
        max_length=120,
        blank=True
    )

    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    compare_at_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    stock = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField (
        default=0,
        editable=False
    )

    review_count = models.PositiveIntegerField (
        default=0, editable=False
    )

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
    is_active = models.BooleanField(
        default=True,
        help_text="Enable or disable this warehouse for inventory operations."
    )

    code = models.CharField(
        max_length=30,
        unique=True
    )

    email = models.EmailField(
        blank=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )

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