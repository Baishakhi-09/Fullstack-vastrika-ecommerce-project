from __future__ import annotations

import json
from typing import Any

from django.conf import settings

from apps.reviews.models import (
    Review,
)


# =========================================================
# REVIEW SCHEMA GENERATOR
# =========================================================
class ReviewSchemaGenerator:
    """
    Generate enterprise-grade
    Review JSON-LD schema.
    """

    DEFAULT_BEST_RATING = "5"

    DEFAULT_WORST_RATING = "1"

    # =====================================================
    # GENERATE SINGLE REVIEW SCHEMA
    # =====================================================
    @classmethod
    def generate(
        cls,
        review: Review,
    ) -> str:

        schema = cls.build_review_schema(
            review,
        )

        cleaned_schema = (
            cls.remove_empty_values(
                schema,
            )
        )

        return json.dumps(
            cleaned_schema,
            indent=4,
            ensure_ascii=False,
        )

    # =====================================================
    # GENERATE MULTIPLE REVIEWS SCHEMA
    # =====================================================
    @classmethod
    def generate_many(
        cls,
        reviews,
    ) -> str:

        schema = {
            "@context": (
                "https://schema.org"
            ),
            "@graph": [
                cls.build_review_schema(
                    review,
                )
                for review
                in reviews
            ],
        }

        cleaned_schema = (
            cls.remove_empty_values(
                schema,
            )
        )

        return json.dumps(
            cleaned_schema,
            indent=4,
            ensure_ascii=False,
        )

    # =====================================================
    # BUILD REVIEW SCHEMA
    # =====================================================
    @classmethod
    def build_review_schema(
        cls,
        review: Review,
    ) -> dict[str, Any]:

        product = getattr(
            review,
            "product",
            None,
        )

        return {
            "@context": (
                "https://schema.org"
            ),
            "@type": "Review",

            # REVIEW BODY
            "reviewBody": (
                cls.get_review_body(
                    review,
                )
            ),

            # REVIEW DATE
            "datePublished": (
                cls.get_review_date(
                    review,
                )
            ),

            # AUTHOR
            "author": {
                "@type": "Person",
                "name": (
                    cls.get_author_name(
                        review,
                    )
                ),
            },

            # REVIEW RATING
            "reviewRating": {
                "@type": "Rating",

                "ratingValue": str(
                    cls.get_rating_value(
                        review,
                    )
                ),

                "bestRating": (
                    cls.DEFAULT_BEST_RATING
                ),

                "worstRating": (
                    cls.DEFAULT_WORST_RATING
                ),
            },

            # ITEM REVIEWED
            "itemReviewed": {
                "@type": "Product",

                "name": (
                    getattr(
                        product,
                        "name",
                        "",
                    )
                ),

                "sku": (
                    getattr(
                        product,
                        "sku",
                        "",
                    )
                ),

                "url": (
                    cls.get_product_url(
                        product,
                    )
                ),
            },
        }

    # =====================================================
    # REVIEW BODY
    # =====================================================
    @staticmethod
    def get_review_body(
        review: Review,
    ) -> str:

        return (
            getattr(
                review,
                "comment",
                "",
            )
            or getattr(
                review,
                "review",
                "",
            )
            or "Product Review"
        )

    # =====================================================
    # REVIEW DATE
    # =====================================================
    @staticmethod
    def get_review_date(
        review: Review,
    ) -> str | None:

        created_at = getattr(
            review,
            "created_at",
            None,
        )

        if not created_at:
            return None

        return created_at.isoformat()

    # =====================================================
    # AUTHOR NAME
    # =====================================================
    @staticmethod
    def get_author_name(
        review: Review,
    ) -> str:

        user = getattr(
            review,
            "user",
            None,
        )

        if not user:
            return "Anonymous"

        full_name = (
            f"{getattr(user, 'first_name', '')} "
            f"{getattr(user, 'last_name', '')}"
        ).strip()

        if full_name:
            return full_name

        return (
            getattr(
                user,
                "email",
                None,
            )
            or "Anonymous"
        )

    # =====================================================
    # RATING VALUE
    # =====================================================
    @staticmethod
    def get_rating_value(
        review: Review,
    ) -> int | float:

        return (
            getattr(
                review,
                "rating",
                0,
            )
            or 0
        )

    # =====================================================
    # PRODUCT URL
    # =====================================================
    @staticmethod
    def get_product_url(
        product,
    ) -> str | None:

        if not product:
            return None

        base_url = getattr(
            settings,
            "SITE_URL",
            "",
        ).rstrip("/")

        slug = getattr(
            product,
            "slug",
            "",
        )

        if not slug:
            return None

        return (
            f"{base_url}/products/"
            f"{slug}/"
        )

    # =====================================================
    # REMOVE EMPTY VALUES
    # =====================================================
    @classmethod
    def remove_empty_values(
        cls,
        data: Any,
    ) -> Any:

        if isinstance(
            data,
            dict,
        ):
            return {
                key: cls.remove_empty_values(
                    value,
                )
                for key, value
                in data.items()
                if value not in (
                    None,
                    "",
                    [],
                    {},
                )
            }

        if isinstance(
            data,
            list,
        ):
            return [
                cls.remove_empty_values(
                    item,
                )
                for item
                in data
                if item not in (
                    None,
                    "",
                    [],
                    {},
                )
            ]

        return data