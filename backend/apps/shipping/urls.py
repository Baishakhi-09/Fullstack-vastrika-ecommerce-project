from django.urls import path

from .views import (
    ShippingRateAPIView,
)

urlpatterns = [
    path(
        "rates/",
        ShippingRateAPIView.as_view(),
        name="shipping-rates",
    ),
]