from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Customer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="customer"
    )
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email or self.user.username

class Review(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="reviews", db_index=True)
    product = models.ForeignKey("products.Product", on_delete=models.PROTECT, related_name="reviews", db_index=True)
    rating = models.PositiveIntegerField(
        default=5,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["product", "created_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["customer", "product"],
                name="unique_customer_product_review"
            )
        ]

    def __str__(self):
        return f"{self.customer} - {self.product} ({self.rating})"