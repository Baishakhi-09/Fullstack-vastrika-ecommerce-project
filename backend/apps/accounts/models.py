from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone

# Create your models here.

# --------------- Custom User Manager --------------- #
class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username field must be set")
        
        email = extra_fields.get("email")
        if email:
            extra_fields["email"] = self.normalize_email(email)

        user = self.model(username=username, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", "admin")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        
        return self.create_user(username, password, **extra_fields)
    
# --------------- Custom User Model --------------- #    
class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(
        unique=True,
        blank=True,
        null=True,
    )
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    alternate_phone = models.CharField(max_length=15, null=True, blank=True)
    address = models.CharField(
        max_length=500,
        blank=True,
        null=True,
    )

    profile_image = models.ImageField(
        upload_to="users/profile/",
        null=True,
        blank=True,
    )

    gender = models.CharField(max_length=20, blank=True, choices=[ ("male", "Male"), ("female", "Female"), ("other", "Other"), ],)

    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True, default="India")

    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("manager", "Manager"),
        ("editor", "Editor"),
        ("user", "User"),
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="user")

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username
    
# --------------- Password Reset OTP Model --------------- #    
class PasswordResetOTP(models.Model):
    phone_number = models.CharField(max_length=20, db_index=True)
    otp_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    is_used = models.BooleanField(default=False)
    attempts = models.PositiveIntegerField(default=0)
    resend_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]

    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"{self.phone_number} | verified={self.is_verified} | used={self.is_used}"
    
# --------------- Newsletter --------------- #
class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-subscribed_at"]
        verbose_name = "Newsletter Subscriber"
        verbose_name_plural = "Newsletter Subscribers"

    def __str__(self):
        return self.email