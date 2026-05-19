from __future__ import annotations

from django.conf import settings
from django.core.validators import (
    RegexValidator,
)
from django.db import models


# =========================================================
# CUSTOMER MODEL
# =========================================================
class Customer(models.Model):
    """
    Extended customer profile model.
    """

    # PHONE VALIDATOR
    phone_validator = RegexValidator(
        regex=r"^[0-9+\-\s()]+$",
        message=(
            "Phone number contains "
            "invalid characters."
        ),
    )

    # USER RELATION
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="customer",
        db_index=True,
    )

    # CUSTOMER DETAILS
    phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[
            phone_validator,
        ],
        db_index=True,
    )

    # STATUS
    is_active = models.BooleanField(
        default=True,
        db_index=True,
    )

    is_verified = (
        models.BooleanField(
            default=False,
            db_index=True,
        )
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

    # META CONFIGURATION
    class Meta:

        db_table = (
            "customers_customer"
        )

        ordering = [
            "-created_at",
        ]

        indexes = [

            models.Index(
                fields=[
                    "created_at",
                ]
            ),

            models.Index(
                fields=[
                    "is_active",
                ]
            ),

            models.Index(
                fields=[
                    "is_verified",
                ]
            ),
        ]

        verbose_name = (
            "Customer"
        )

        verbose_name_plural = (
            "Customers"
        )

    # STRING REPRESENTATION
    def __str__(
        self,
    ) -> str:

        return (
            self.user.email
            or self.user.username
            or f"Customer #{self.pk}"
        )

    # FULL NAME
    @property
    def full_name(
        self,
    ) -> str:

        full_name = (
            f"{self.user.first_name} "
            f"{self.user.last_name}"
        ).strip()

        return (
            full_name
            or self.user.username
        )

    # EMAIL
    @property
    def email(
        self,
    ) -> str:

        return (
            self.user.email
        )

    # PHONE NORMALIZATION
    def save(
        self,
        *args,
        **kwargs,
    ) -> None:

        if self.phone:
            self.phone = (
                self.phone.strip()
            )

        super().save(
            *args,
            **kwargs,
        )