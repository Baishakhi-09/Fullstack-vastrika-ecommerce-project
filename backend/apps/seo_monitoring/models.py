from __future__ import annotations

from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models


# =========================================================
# KEYWORD RANKING MODEL
# =========================================================
class KeywordRanking(models.Model):
    """
    Stores SEO keyword ranking analytics.
    """

    # SEARCH ENGINE CHOICES
    class SearchEngine(models.TextChoices):
        GOOGLE = (
            "google",
            "Google",
        )

        BING = (
            "bing",
            "Bing",
        )

        YAHOO = (
            "yahoo",
            "Yahoo",
        )

    # DEVICE TYPE CHOICES
    class DeviceType(models.TextChoices):
        MOBILE = (
            "mobile",
            "Mobile",
        )

        DESKTOP = (
            "desktop",
            "Desktop",
        )

        TABLET = (
            "tablet",
            "Tablet",
        )

    # KEYWORD INFORMATION
    keyword = models.CharField(
        max_length=255,
        db_index=True,
        help_text=(
            "Tracked SEO keyword."
        ),
    )

    landing_page = models.URLField(
        blank=True,
        help_text=(
            "Landing page URL "
            "ranking for keyword."
        ),
    )

    search_engine = models.CharField(
        max_length=20,
        choices=SearchEngine.choices,
        default=SearchEngine.GOOGLE,
        db_index=True,
    )

    device_type = models.CharField(
        max_length=20,
        choices=DeviceType.choices,
        default=DeviceType.DESKTOP,
        db_index=True,
    )

    country = models.CharField(
        max_length=10,
        default="IN",
        db_index=True,
        help_text=(
            "Country code "
            "(ISO format)."
        ),
    )

    # SEO METRICS
    ranking_position = (
        models.PositiveIntegerField(
            validators=[
                MinValueValidator(1),
            ],
            help_text=(
                "SERP ranking position."
            ),
        )
    )

    impressions = (
        models.PositiveIntegerField(
            default=0,
        )
    )

    clicks = (
        models.PositiveIntegerField(
            default=0,
        )
    )

    ctr = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
        help_text=(
            "Click-through rate percentage."
        ),
    )

    # TIMESTAMPS
    recorded_at = (
        models.DateTimeField(
            auto_now_add=True,
            db_index=True,
        )
    )

    updated_at = (
        models.DateTimeField(
            auto_now=True,
        )
    )

    # META CONFIGURATION
    class Meta:

        db_table = (
            "seo_monitoring_keyword_ranking"
        )

        ordering = [
            "-recorded_at",
        ]

        indexes = [

            models.Index(
                fields=[
                    "keyword",
                    "search_engine",
                ]
            ),

            models.Index(
                fields=[
                    "keyword",
                    "country",
                ]
            ),

            models.Index(
                fields=[
                    "recorded_at",
                ]
            ),

            models.Index(
                fields=[
                    "ranking_position",
                ]
            ),
        ]

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "keyword",
                    "search_engine",
                    "device_type",
                    "country",
                    "recorded_at",
                ],
                name=(
                    "unique_keyword_tracking"
                ),
            ),
        ]

        verbose_name = (
            "Keyword Ranking"
        )

        verbose_name_plural = (
            "Keyword Rankings"
        )

    # STRING REPRESENTATION
    def __str__(
        self,
    ) -> str:

        return (
            f"{self.keyword} | "
            f"{self.search_engine} | "
            f"#{self.ranking_position}"
        )

    # NORMALIZATION
    def save(
        self,
        *args,
        **kwargs,
    ) -> None:

        # NORMALIZE KEYWORD
        self.keyword = (
            self.keyword.strip().lower()
        )

        # NORMALIZE COUNTRY
        self.country = (
            self.country.strip().upper()
        )

        super().save(
            *args,
            **kwargs,
        )

    # HELPER PROPERTY
    @property
    def is_top_10(
        self,
    ) -> bool:

        return (
            self.ranking_position <= 10
        )