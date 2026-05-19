from __future__ import annotations

from django.conf import settings
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils.text import slugify


# =========================================================
# REVIEW MODEL
# =========================================================
class Review(models.Model):

    # REVIEW STATUS
    class Status(models.TextChoices):
        PENDING = (
            "pending",
            "Pending",
        )

        APPROVED = (
            "approved",
            "Approved",
        )

        REJECTED = (
            "rejected",
            "Rejected",
        )

    # RELATIONS
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="reviews",
        db_index=True,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        db_index=True,
    )

    # REVIEW CONTENT
    title = models.CharField(
        max_length=255,
        blank=True,
    )

    comment = models.TextField()

    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
        db_index=True,
    )

    # REVIEW STATUS
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    # VERIFIED PURCHASE
    is_verified_purchase = (
        models.BooleanField(
            default=False,
        )
    )

    # HELPFUL COUNTER
    helpful_count = (
        models.PositiveIntegerField(
            default=0,
        )
    )

    # SLUG
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
    )

    # TIMESTAMPS
    created_at = (
        models.DateTimeField(
            auto_now_add=True,
            db_index=True,
        )
    )

    updated_at = (
        models.DateTimeField(
            auto_now=True,
        )
    )

    # =====================================================
    # META CONFIG
    # =====================================================
    class Meta:

        db_table = (
            "product_reviews"
        )

        ordering = [
            "-created_at",
        ]

        indexes = [
            models.Index(
                fields=[
                    "product",
                    "status",
                ]
            ),

            models.Index(
                fields=[
                    "user",
                    "created_at",
                ]
            ),

            models.Index(
                fields=[
                    "rating",
                ]
            ),
        ]

        constraints = [

            # ONE REVIEW PER USER
            models.UniqueConstraint(
                fields=[
                    "product",
                    "user",
                ],
                name=(
                    "unique_review_per_user"
                ),
            ),
        ]

        verbose_name = (
            "Review"
        )

        verbose_name_plural = (
            "Reviews"
        )

    # STRING REPRESENTATION
    def __str__(
        self,
    ) -> str:

        return (
            f"{self.product} | "
            f"{self.user} | "
            f"{self.rating}★"
        )

    # SAVE METHOD
    def save(
        self,
        *args,
        **kwargs,
    ) -> None:

        if not self.slug:

            base_slug = slugify(
                (
                    f"{self.product_id}-"
                    f"{self.user_id}-"
                    f"{self.rating}"
                )
            )

            slug = base_slug
            counter = 1

            while (
                Review.objects.filter(
                    slug=slug
                )
                .exclude(
                    pk=self.pk
                )
                .exists()
            ):
                slug = (
                    f"{base_slug}-"
                    f"{counter}"
                )

                counter += 1

            self.slug = slug

        super().save(
            *args,
            **kwargs,
        )

    # APPROVAL CHECK
    @property
    def is_approved(
        self,
    ) -> bool:

        return (
            self.status
            == self.Status.APPROVED
        )

    # JSON SERIALIZATION
    def to_dict(
        self,
    ) -> dict:

        return {
            "id": self.id,
            "product_id": (
                self.product_id
            ),
            "user_id": (
                self.user_id
            ),
            "title": self.title,
            "comment": self.comment,
            "rating": self.rating,
            "status": self.status,
            "is_verified_purchase": (
                self.is_verified_purchase
            ),
            "helpful_count": (
                self.helpful_count
            ),
            "created_at": (
                self.created_at.isoformat()
            ),
        }