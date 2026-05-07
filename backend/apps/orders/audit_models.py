from django.db import models
from django.conf import settings


class OrderActivityLog(models.Model):
    class Action(models.TextChoices):
        CREATED = "created", "Created"
        STATUS_CHANGED = "status_changed", "Status Changed"
        CANCELLED = "cancelled", "Cancelled"
        RETURN_UPDATED = "return_updated", "Return Updated"
        REFUNDED = "refunded", "Refunded"
        NOTE = "note", "Note"

    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="activity_logs",
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_activity_logs",
    )

    action = models.CharField(
        max_length=50,
        choices=Action.choices,
        default=Action.NOTE,
        db_index=True,
    )

    message = models.TextField()

    old_status = models.CharField(max_length=50, blank=True)
    new_status = models.CharField(max_length=50, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["order", "created_at"]),
            models.Index(fields=["actor", "created_at"]),
        ]

    def __str__(self):
        date = self.created_at.strftime("%d %b %Y") if self.created_at else ""
        return f"{self.order} | {self.get_action_display()} | {date}"