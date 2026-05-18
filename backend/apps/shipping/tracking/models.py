from django.db import models



class ShipmentTracking(models.Model):

    tracking_number = models.CharField(max_length=255)

    courier = models.CharField(max_length=100)
    status = models.CharField(max_length=100)

    location = models.CharField(
        max_length=255,
        blank=True,
    )

    updated_at = models.DateTimeField(auto_now=True)