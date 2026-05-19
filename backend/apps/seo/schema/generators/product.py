from __future__ import annotations

import json
from typing import Any

from django.conf import settings
from django.templatetags.static import static

from apps.products.models import (
    Product,
)


# =========================================================
# PRODUCT SCHEMA GENERATOR
# =========================================================
class ProductSchemaGenerator:
    """
    Generate enterprise-grade
    Product JSON-LD schema.
    """

    DEFAULT_CURRENCY = "INR"

    DEFAULT_BRAND = (
        "Vastrika"
    )

    # =====================================================
    # GENERATE PRODUCT SCHEMA
    # =====================================================
    @classmethod
    def generate(
        cls,
        product: Product,
    ) -> str:

        schema = {
            "@context": (
                "https://schema.org"
            ),
            "@type": "Product",

            # BASIC INFO
            "name": (
                product.name
            ),

            "description": (
                cls.get_description(
                    product,
                )
            ),

            "sku": (
                product.sku
            ),

            "url": (
                cls.get_product_url(
                    product,
                )
            ),

            "category": (
                cls.get_category(
                    product,
                )
            ),

            # BRAND
            "brand": {
                "@type": "Brand",
                "name": (
                    cls.get_brand_name(
                        product,
                    )
                ),
            },

            # IMAGES
            "image": (
                cls.get_product_images(
                    product,
                )
            ),

            # OFFERS
            "offers": {
                "@type": "Offer",

                "url": (
                    cls.get_product_url(
                        product,
                    )
                ),

                "priceCurrency": (
                    cls.DEFAULT_CURRENCY
                ),

                "price": str(
                    (
                        product.selling_price
                        or 0
                    )
                ),

                "availability": (
                    cls.get_availability(
                        product,
                    )
                ),

                "itemCondition": (
                    "https://schema.org/"
                    "NewCondition"
                ),

                "seller": {
                    "@type": (
                        "Organization"
                    ),
                    "name": (
                        cls.DEFAULT_BRAND
                    ),
                },
            },
        }

        # OPTIONAL RATINGS
        aggregate_rating = (
            cls.get_aggregate_rating(
                product,
            )
        )

        if aggregate_rating:
            schema[
                "aggregateRating"
            ] = aggregate_rating

        # REMOVE EMPTY VALUES
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
    # PRODUCT DESCRIPTION
    # =====================================================
    @staticmethod
    def get_description(
        product: Product,
    ) -> str:

        return (
            product.meta_description
            or getattr(
                product,
                "short_description",
                "",
            )
            or getattr(
                product,
                "description",
                "",
            )
            or product.name
        )

    # =====================================================
    # PRODUCT URL
    # =====================================================
    @staticmethod
    def get_product_url(
        product: Product,
    ) -> str:

        base_url = getattr(
            settings,
            "SITE_URL",
            "",
        ).rstrip("/")

        return (
            f"{base_url}/products/"
            f"{product.slug}/"
        )

    # =====================================================
    # CATEGORY
    # =====================================================
    @staticmethod
    def get_category(
        product: Product,
    ) -> str | None:

        category = getattr(
            product,
            "parent_category",
            None,
        )

        if not category:
            return None

        return str(category)

    # =====================================================
    # BRAND NAME
    # =====================================================
    @classmethod
    def get_brand_name(
        cls,
        product: Product,
    ) -> str:

        brand = getattr(
            product,
            "brand",
            None,
        )

        if brand:
            return str(brand.name)

        return cls.DEFAULT_BRAND

    # =====================================================
    # PRODUCT IMAGES
    # =====================================================
    @staticmethod
    def get_product_images(
        product: Product,
    ) -> list[str]:

        images: list[str] = []

        base_url = getattr(
            settings,
            "SITE_URL",
            "",
        ).rstrip("/")

        # MAIN IMAGE
        product_image = getattr(
            product,
            "image",
            None,
        )

        if (
            product_image
            and hasattr(
                product_image,
                "url",
            )
        ):
            images.append(
                (
                    f"{base_url}"
                    f"{product_image.url}"
                )
            )

        # FALLBACK IMAGE
        if not images:
            images.append(
                (
                    f"{base_url}"
                    f"{static('images/no-image.png')}"
                )
            )

        return images

    # =====================================================
    # PRODUCT AVAILABILITY
    # =====================================================
    @staticmethod
    def get_availability(
        product: Product,
    ) -> str:

        total_stock = 0

        variants = getattr(
            product,
            "variants",
            None,
        )

        if variants:

            total_stock = sum(
                (
                    variant.stock
                    or 0
                )
                for variant
                in variants.all()
            )

        if total_stock > 0:
            return (
                "https://schema.org/"
                "InStock"
            )

        return (
            "https://schema.org/"
            "OutOfStock"
        )

    # =====================================================
    # AGGREGATE RATING
    # =====================================================
    @staticmethod
    def get_aggregate_rating(
        product: Product,
    ) -> dict[str, Any] | None:

        average_rating = getattr(
            product,
            "average_rating",
            None,
        )

        total_reviews = getattr(
            product,
            "review_count",
            None,
        )

        if (
            average_rating is None
            or not total_reviews
        ):
            return None

        return {
            "@type": (
                "AggregateRating"
            ),
            "ratingValue": str(
                average_rating
            ),
            "reviewCount": str(
                total_reviews
            ),
            "bestRating": "5",
            "worstRating": "1",
        }

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