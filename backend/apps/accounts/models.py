from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
)
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


# VALIDATORS
phone_validator = RegexValidator(
    regex=r"^\+?[0-9]{10,15}$",
    message=(
        "Phone number must contain only digits "
        "and be between 10 to 15 characters."
    ),
)


# USER MANAGER
class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(
        self,
        username: str,
        password: str | None = None,
        **extra_fields: Any,
    ) -> User:
        """
        Create and return a regular user.
        """

        if not username:
            raise ValueError(
                "The username field must be set."
            )

        username = username.strip()

        email = extra_fields.get("email")

        if email:
            extra_fields["email"] = self.normalize_email(
                email,
            )

        phone = extra_fields.get("phone")

        if phone:
            extra_fields["phone"] = str(phone).strip()

        user = self.model(
            username=username,
            **extra_fields,
        )

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)

        return user

    def create_superuser(
        self,
        username: str,
        password: str | None = None,
        **extra_fields: Any,
    ) -> User:
        """
        Create and return a superuser.
        """

        extra_fields.setdefault(
            "is_staff",
            True,
        )

        extra_fields.setdefault(
            "is_superuser",
            True,
        )

        extra_fields.setdefault(
            "is_active",
            True,
        )

        extra_fields.setdefault(
            "role",
            User.Role.ADMIN,
        )

        if extra_fields.get("is_staff") is not True:
            raise ValueError(
                "Superuser must have is_staff=True."
            )

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(
                "Superuser must have is_superuser=True."
            )

        return self.create_user(
            username=username,
            password=password,
            **extra_fields,
        )


# USER MODEL
class User(AbstractUser):

    # ENUMS
    class Gender(models.TextChoices):

        MALE = "male", "Male"
        FEMALE = "female", "Female"
        OTHER = "other", "Other"

    class Role(models.TextChoices):

        ADMIN = "admin", "Admin"
        MANAGER = "manager", "Manager"
        EDITOR = "editor", "Editor"
        USER = "user", "User"

    # BASIC INFORMATION
    username = models.CharField(
        max_length=150,
        unique=True,
        db_index=True,
    )

    email = models.EmailField(
        unique=True,
        blank=True,
        null=True,
        db_index=True,
    )

    phone = models.CharField(
        max_length=15,
        unique=True,
        blank=True,
        null=True,
        validators=[phone_validator],
        db_index=True,
    )

    alternate_phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[phone_validator],
    )

    gender = models.CharField(
        max_length=20,
        choices=Gender.choices,
        blank=True,
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
        db_index=True,
    )

    # PROFILE
    profile_image = models.ImageField(
        upload_to="users/profile/",
        blank=True,
        null=True,
    )

    # ADDRESS
    address = models.CharField(
        max_length=500,
        blank=True,
        null=True,
    )

    address_line_1 = models.CharField(
        max_length=255,
        blank=True,
    )

    address_line_2 = models.CharField(
        max_length=255,
        blank=True,
    )

    city = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
    )

    state = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
    )

    pincode = models.CharField(
        max_length=20,
        blank=True,
        db_index=True,
    )

    country = models.CharField(
        max_length=100,
        blank=True,
        default="India",
    )

    # TIMESTAMPS
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    # MANAGER
    objects = UserManager()

    # AUTH SETTINGS
    USERNAME_FIELD = "username"

    REQUIRED_FIELDS: list[str] = []

    # META
    class Meta:

        ordering = ["-created_at"]

        verbose_name = "User"

        verbose_name_plural = "Users"

        indexes = [
            models.Index(fields=["username"]),
            models.Index(fields=["email"]),
            models.Index(fields=["phone"]),
            models.Index(fields=["role"]),
            models.Index(fields=["created_at"]),
        ]

    # METHODS
    def __str__(self) -> str:
        return self.username


# PASSWORD RESET OTP
class PasswordResetOTP(models.Model):
    phone_number = models.CharField(
        max_length=20,
        db_index=True,
        validators=[phone_validator],
    )

    otp_hash = models.CharField(
        max_length=128,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    expires_at = models.DateTimeField(
        db_index=True,
    )

    is_verified = models.BooleanField(
        default=False,
    )

    is_used = models.BooleanField(
        default=False,
    )

    attempts = models.PositiveIntegerField(
        default=0,
    )

    resend_count = models.PositiveIntegerField(
        default=0,
    )

    # META
    class Meta:

        ordering = ["-created_at"]

        verbose_name = "Password Reset OTP"

        verbose_name_plural = (
            "Password Reset OTPs"
        )

        indexes = [
            models.Index(fields=["phone_number"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["created_at"]),
        ]

    # METHODS
    def is_expired(self) -> bool:
        """
        Check whether OTP is expired.
        """

        return timezone.now() > self.expires_at

    @classmethod
    def default_expiry(cls) -> timezone.datetime:
        """
        Return default OTP expiry time.
        """

        return timezone.now() + timedelta(
            minutes=10,
        )

    def __str__(self) -> str:

        return (
            f"{self.phone_number} | "
            f"verified={self.is_verified} | "
            f"used={self.is_used}"
        )


# NEWSLETTER SUBSCRIBER
class NewsletterSubscriber(models.Model):
    email = models.EmailField(
        unique=True,
        db_index=True,
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
    )

    subscribed_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    # META
    class Meta:

        ordering = ["-subscribed_at"]

        verbose_name = "Newsletter Subscriber"

        verbose_name_plural = (
            "Newsletter Subscribers"
        )

        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["subscribed_at"]),
        ]

    # METHODS
    def __str__(self) -> str:
        return self.email