from django.apps import AppConfig


# =========================================================
# REVIEWS APP CONFIG
# =========================================================
class ReviewsConfig(
    AppConfig,
):
    default_auto_field = (
        "django.db.models.BigAutoField"
    )

    name = (
        "apps.reviews"
    )

    verbose_name = (
        "Reviews"
    )