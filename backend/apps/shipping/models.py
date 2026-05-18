from django.db import models

class Shipment(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("in_transit", "In Transit"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    order_id = models.CharField(max_length=255)

    courier = models.CharField(max_length=100)

    tracking_number = models.CharField(max_length=255)

    shipping_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    estimated_delivery = models.DateField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="pending",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.order_id} - {self.courier}"