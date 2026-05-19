from __future__ import annotations

from django.core.validators import (
    RegexValidator,
)
from django.db import models


# =========================================================
# WAREHOUSE MODEL
# =========================================================
class Warehouse(models.Model):
    """
    Warehouse management model.
    """

    # =====================================================
    # STATUS CHOICES
    # =====================================================
    class Status(models.TextChoices):

        ACTIVE = (
            "active",
            "Active",
        )

        MAINTENANCE = (
            "maintenance",
            "Maintenance",
        )

        CLOSED = (
            "closed",
            "Closed",
        )

    # =====================================================
    # VALIDATORS
    # =====================================================
    phone_validator = RegexValidator(
        regex=r"^[0-9+\-\s()]+$",
        message=(
            "Phone number contains "
            "invalid characters."
        ),
    )

    # =====================================================
    # BASIC INFORMATION
    # =====================================================
    name = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text=(
            "Warehouse name."
        ),
    )

    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text=(
            "Unique warehouse code."
        ),
    )

    # =====================================================
    # LOCATION INFORMATION
    # =====================================================
    address = models.TextField(
        blank=True,
        help_text=(
            "Warehouse address."
        ),
    )

    city = models.CharField(
        max_length=255,
        db_index=True,
    )

    state = models.CharField(
        max_length=255,
        db_index=True,
    )

    country = models.CharField(
        max_length=255,
        db_index=True,
    )

    postal_code = models.CharField(
        max_length=20,
        blank=True,
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    # =====================================================
    # CONTACT INFORMATION
    # =====================================================
    contact_person = models.CharField(
        max_length=255,
        blank=True,
    )

    contact_email = models.EmailField(
        blank=True,
    )

    contact_phone = models.CharField(
        max_length=30,
        blank=True,
        validators=[
            phone_validator,
        ],
    )

    # =====================================================
    # WAREHOUSE STATUS
    # =====================================================
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )

    is_default = models.BooleanField(
        default=False,
        db_index=True,
        help_text=(
            "Default warehouse "
            "for fulfillment."
        ),
    )

    # =====================================================
    # OPERATIONAL DATA
    # =====================================================
    capacity = models.PositiveIntegerField(
        default=0,
        help_text=(
            "Maximum storage capacity."
        ),
    )

    current_stock = (
        models.PositiveIntegerField(
            default=0,
            help_text=(
                "Current stock volume."
            ),
        )
    )

    # =====================================================
    # TIMESTAMPS
    # =====================================================
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
    # META CONFIGURATION
    # =====================================================
    class Meta:

        db_table = (
            "warehouses"
        )

        ordering = [
            "name",
        ]

        indexes = [

            models.Index(
                fields=[
                    "city",
                    "country",
                ]
            ),

            models.Index(
                fields=[
                    "status",
                ]
            ),

            models.Index(
                fields=[
                    "is_default",
                ]
            ),
        ]

        verbose_name = (
            "Warehouse"
        )

        verbose_name_plural = (
            "Warehouses"
        )

    # =====================================================
    # STRING REPRESENTATION
    # =====================================================
    def __str__(
        self,
    ) -> str:

        return (
            f"{self.name} "
            f"({self.code})"
        )

    # =====================================================
    # SAVE NORMALIZATION
    # =====================================================
    def save(
        self,
        *args,
        **kwargs,
    ) -> None:

        # NORMALIZE STRINGS
        self.name = (
            self.name.strip()
        )

        self.code = (
            self.code.strip().upper()
        )

        self.city = (
            self.city.strip().title()
        )

        self.state = (
            self.state.strip().title()
        )

        self.country = (
            self.country.strip().title()
        )

        # ENSURE SINGLE DEFAULT
        if self.is_default:

            Warehouse.objects.exclude(
                pk=self.pk
            ).update(
                is_default=False
            )

        super().save(
            *args,
            **kwargs,
        )

    # =====================================================
    # HELPER PROPERTY
    # =====================================================
    @property
    def full_address(
        self,
    ) -> str:

        parts = [

            self.address,
            self.city,
            self.state,
            self.country,
            self.postal_code,
        ]

        return ", ".join(
            filter(
                None,
                parts,
            )
        )

    # =====================================================
    # CAPACITY CHECK
    # =====================================================
    @property
    def available_capacity(
        self,
    ) -> int:

        return max(
            self.capacity
            - self.current_stock,
            0,
        )