from django.db import models


class Warehouse(models.Model):
    name = models.CharField(max_length=255)

    city = models.CharField(max_length=255)

    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255)

    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name