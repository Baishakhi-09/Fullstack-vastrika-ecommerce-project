from typing import Any

from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
)
from django.db import models
from django.utils import timezone

from .constants import UserRole

PHONE_MAX_LENGTH = 15
GENDER_MAX_LENGTH = 20
ADDRESS_MAX_LENGTH = 500
ADDRESS_LINE_MAX_LENGTH = 255
PINCODE_MAX_LENGTH = 20
CITY_MAX_LENGTH = 100
STATE_MAX_LENGTH = 100
COUNTRY_MAX_LENGTH = 100


# Abstract reusable timestamp model.
class TimeStampedModel(models.Model):
    """
    Abstract base model with timestamps.
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        abstract = True

# =========================================================
# CUSTOM USER MANAGER
# =========================================================

class UserManager(BaseUserManager):
    """
    Custom user manager for application users.
    """

    def create_user(
        self,
        username: str,
        password: str | None = None,
        **extra_fields: Any,
    ) -> "User":

        if not username:
            raise ValueError(
                "The Username field must be set."
            )

        email = extra_fields.get("email")

        if email:
            extra_fields["email"] = (
                self.normalize_email(email)
            )

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
    ) -> "User":

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
            "admin",
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
            username,
            password,
            **extra_fields,
        )


# =========================================================
# CUSTOM USER MODEL
# =========================================================

class User(AbstractUser):
    """
    Custom application user model.
    """

    GENDER_CHOICES = (
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    )

    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("manager", "Manager"),
        ("editor", "Editor"),
        ("user", "User"),
    )

    username = models.CharField(
        max_length=150,
        unique=True,
    )

    email = models.EmailField(
        unique=True,
        db_index=True,
        help_text="Unique user email address.",
    )

    phone = models.CharField(
        max_length=PHONE_MAX_LENGTH,
        unique=True,
        db_index=True,
        null=True,
        blank=True,
        help_text="Primary contact number.",
    )

    alternate_phone = models.CharField(
        max_length=PHONE_MAX_LENGTH,
        null=True,
        blank=True,
        help_text="Secondary contact number.",
    )

    address = models.CharField(
        max_length=ADDRESS_MAX_LENGTH,
        blank=True,
        null=True,
    )

    profile_image = models.ImageField(
        upload_to="users/profile/",
        null=True,
        blank=True,
        help_text="Upload user profile image.",
    )

    gender = models.CharField(
        max_length=GENDER_MAX_LENGTH,
        blank=True,
        choices=GENDER_CHOICES,
    )

    address_line_1 = models.CharField(
        max_length=ADDRESS_LINE_MAX_LENGTH,
        blank=True,
    )

    address_line_2 = models.CharField(
        max_length=ADDRESS_LINE_MAX_LENGTH,
        blank=True,
    )

    city = models.CharField(
        max_length=CITY_MAX_LENGTH,
        blank=True,
    )

    state = models.CharField(
        max_length=STATE_MAX_LENGTH,
        blank=True,
    )

    pincode = models.CharField(
        max_length=PINCODE_MAX_LENGTH,
        blank=True,
    )

    country = models.CharField(
        max_length=COUNTRY_MAX_LENGTH,
        blank=True,
        default="India",
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default="user",
        db_index=True,
        help_text="Select user access role.",
    )

    objects = UserManager()

    USERNAME_FIELD = "username"

    REQUIRED_FIELDS = [
        "email",
    ]

    class Meta:
        db_table = "accounts_users"
        ordering = ["-id"]

        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self) -> str:
        return self.username


# =========================================================
# PASSWORD RESET OTP MODEL
# =========================================================

class PasswordResetOTP(TimeStampedModel):
    """
    Stores password reset OTP verification records.
    """

    phone_number = models.CharField(
        max_length=PHONE_MAX_LENGTH,
        db_index=True,
    )

    otp_hash = models.CharField(
        max_length=128,
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

    class Meta:
        db_table = "accounts_password_reset_otps"

        ordering = [
            "-created_at",
        ]

        indexes = [
            models.Index(
                fields=["phone_number"],
            ),

            models.Index(
                fields=["expires_at"],
            ),

            models.Index(
                fields=[
                    "phone_number",
                    "expires_at",
                ],
            ),
        ]

        constraints = [
            models.CheckConstraint(
                check=models.Q(attempts__gte=0),
                name="otp_attempts_non_negative",
            ),

            models.CheckConstraint(
                check=models.Q(resend_count__gte=0),
                name="otp_resend_count_non_negative",
            ),
        ]

        verbose_name = "Password Reset OTP"

        verbose_name_plural = (
            "Password Reset OTPs"
        )

    def is_expired(self) -> bool:
        return (
            timezone.now() > self.expires_at
        )

    def __str__(self) -> str:
        return (
            f"{self.phone_number} | "
            f"verified={self.is_verified} | "
            f"used={self.is_used}"
        )
    
    @classmethod
    def cleanup_expired_otps(cls) -> int:
        """
        Delete expired OTP records.
        """

        deleted_count, _ = cls.objects.filter(
            expires_at__lt=timezone.now(),
        ).delete()

        return deleted_count
    
    
class NewsletterSubscriberQuerySet(
    models.QuerySet["NewsletterSubscriber"],
):
    """
    Custom queryset for newsletter subscribers.
    """

    def active(
        self,
    ) -> "NewsletterSubscriberQuerySet":
        
        return self.filter(
            is_active=True,
        )

# =========================================================
# NEWSLETTER SUBSCRIBER MODEL
# =========================================================

class NewsletterSubscriber(TimeStampedModel):
    """
    Stores newsletter subscriber information.
    """

    objects: models.Manager[
        "NewsletterSubscriber"
    ] = (
        NewsletterSubscriberQuerySet
        .as_manager()
    )

    email = models.EmailField(
        unique=True,
        db_index=True,
        help_text="Unique user email address.",
    )

    is_active = models.BooleanField(
        default=True,
    )

    subscribed_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        db_table = "accounts_newsletter_subscribers"

        ordering = [
            "-updated_at",
        ]

        verbose_name = (
            "Newsletter Subscriber"
        )

        verbose_name_plural = (
            "Newsletter Subscribers"
        )

    def __str__(self) -> str:
        return self.email