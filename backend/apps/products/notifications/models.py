from django.db import models
from django.conf import settings

class AdminNotification(models.Model):
    class Type(models.TextChoices):
        ORDER = "order", "Order"
        PRODUCT = "product", "Product"
        CUSTOMER = "customer", "Customer"
        STOCK = "stock", "Stock"
        SYSTEM = "system", "System"

    title = models.CharField(max_length=150)
    message = models.TextField()

    notification_type = models.CharField(
        max_length=30,
        choices=Type.choices,
        default=Type.SYSTEM,
        db_index=True,
    )

    url = models.CharField(max_length=500, blank=True, null=True)
    
    created_for = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="admin_notifications",
        null=True,
        blank=True,
        db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products_admin_notification"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_for"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.notification_type})"
    
class AdminNotificationRead(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_reads",
    )

    notification = models.ForeignKey(
        AdminNotification,
        on_delete=models.CASCADE,
        related_name="reads",
    )

    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "products_admin_notification_read"
        unique_together = ("user", "notification")
        indexes = [
            models.Index(fields=["user", "notification"]),
        ]

    def __str__(self):
        return f"{self.user} read {self.notification}"