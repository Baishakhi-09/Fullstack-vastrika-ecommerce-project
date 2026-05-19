from __future__ import annotations

import logging

from django.db import (
    transaction,
)
from django.db.models.signals import (
    post_delete,
    post_save,
    pre_save,
)
from django.dispatch import (
    receiver,
)

from apps.products.models import (
    CartItem,
    Product,
    ProductVariant,
    WishlistItem,
)


logger = logging.getLogger(
    __name__
)


# =========================================================
# PRODUCT SIGNALS
# =========================================================
@receiver(
    pre_save,
    sender=Product,
)
def store_old_product_state(
    sender,
    instance: Product,
    **kwargs,
) -> None:
    """
    Store previous product state
    before update.
    """

    if not instance.pk:
        instance._old_instance = None
        return

    instance._old_instance = (
        Product.objects.filter(
            pk=instance.pk,
        )
        .only(
            "id",
            "name",
            "selling_price",
            "is_active",
            "is_featured",
            "is_best_seller",
        )
        .first()
    )


@receiver(
    post_save,
    sender=Product,
)
def product_post_save(
    sender,
    instance: Product,
    created: bool,
    **kwargs,
) -> None:
    """
    Handle product create/update events.
    """

    def log_product_event() -> None:

        # PRODUCT CREATED
        if created:

            logger.info(
                (
                    "Product created | "
                    "ID=%s | "
                    "Name=%s | "
                    "SKU=%s"
                ),
                instance.id,
                instance.name,
                instance.sku,
            )

            return

        old_instance = getattr(
            instance,
            "_old_instance",
            None,
        )

        if not old_instance:
            return

        # PRICE UPDATED
        if (
            old_instance.selling_price
            != instance.selling_price
        ):
            logger.info(
                (
                    "Product price updated | "
                    "Product=%s | "
                    "Old=%s | "
                    "New=%s"
                ),
                instance.name,
                old_instance.selling_price,
                instance.selling_price,
            )

        # ACTIVE STATUS UPDATED
        if (
            old_instance.is_active
            != instance.is_active
        ):
            logger.info(
                (
                    "Product active status changed | "
                    "Product=%s | "
                    "Old=%s | "
                    "New=%s"
                ),
                instance.name,
                old_instance.is_active,
                instance.is_active,
            )

        # FEATURED STATUS UPDATED
        if (
            old_instance.is_featured
            != instance.is_featured
        ):
            logger.info(
                (
                    "Product featured status changed | "
                    "Product=%s | "
                    "Old=%s | "
                    "New=%s"
                ),
                instance.name,
                old_instance.is_featured,
                instance.is_featured,
            )

        # BEST SELLER UPDATED
        if (
            old_instance.is_best_seller
            != instance.is_best_seller
        ):
            logger.info(
                (
                    "Product best seller status changed | "
                    "Product=%s | "
                    "Old=%s | "
                    "New=%s"
                ),
                instance.name,
                old_instance.is_best_seller,
                instance.is_best_seller,
            )

    transaction.on_commit(
        log_product_event
    )


@receiver(
    post_delete,
    sender=Product,
)
def product_post_delete(
    sender,
    instance: Product,
    **kwargs,
) -> None:
    """
    Handle product deletion events.
    """

    transaction.on_commit(
        lambda: logger.warning(
            (
                "Product deleted | "
                "ID=%s | "
                "Name=%s | "
                "SKU=%s"
            ),
            instance.id,
            instance.name,
            instance.sku,
        )
    )


# =========================================================
# PRODUCT VARIANT SIGNALS
# =========================================================
@receiver(
    pre_save,
    sender=ProductVariant,
)
def store_old_variant_state(
    sender,
    instance: ProductVariant,
    **kwargs,
) -> None:
    """
    Store previous variant state
    before update.
    """

    if not instance.pk:
        instance._old_instance = None
        return

    instance._old_instance = (
        ProductVariant.objects.filter(
            pk=instance.pk,
        )
        .only(
            "id",
            "stock",
            "reserved_stock",
            "is_active",
        )
        .first()
    )


@receiver(
    post_save,
    sender=ProductVariant,
)
def product_variant_post_save(
    sender,
    instance: ProductVariant,
    created: bool,
    **kwargs,
) -> None:
    """
    Handle product variant updates.
    """

    def log_variant_event() -> None:

        if created:

            logger.info(
                (
                    "Product variant created | "
                    "Variant=%s | "
                    "Product=%s"
                ),
                instance.variant_sku,
                instance.product.name,
            )

            return

        old_instance = getattr(
            instance,
            "_old_instance",
            None,
        )

        if not old_instance:
            return

        # STOCK UPDATED
        if (
            old_instance.stock
            != instance.stock
        ):
            logger.info(
                (
                    "Variant stock updated | "
                    "Variant=%s | "
                    "Old=%s | "
                    "New=%s"
                ),
                instance.variant_sku,
                old_instance.stock,
                instance.stock,
            )

        # RESERVED STOCK UPDATED
        if (
            old_instance.reserved_stock
            != instance.reserved_stock
        ):
            logger.info(
                (
                    "Variant reserved stock updated | "
                    "Variant=%s | "
                    "Old=%s | "
                    "New=%s"
                ),
                instance.variant_sku,
                old_instance.reserved_stock,
                instance.reserved_stock,
            )

        # ACTIVE STATUS UPDATED
        if (
            old_instance.is_active
            != instance.is_active
        ):
            logger.info(
                (
                    "Variant active status changed | "
                    "Variant=%s | "
                    "Old=%s | "
                    "New=%s"
                ),
                instance.variant_sku,
                old_instance.is_active,
                instance.is_active,
            )

    transaction.on_commit(
        log_variant_event
    )


@receiver(
    post_delete,
    sender=ProductVariant,
)
def product_variant_post_delete(
    sender,
    instance: ProductVariant,
    **kwargs,
) -> None:
    """
    Handle variant deletion events.
    """

    transaction.on_commit(
        lambda: logger.warning(
            (
                "Product variant deleted | "
                "Variant=%s | "
                "Product=%s"
            ),
            instance.variant_sku,
            instance.product.name,
        )
    )


# =========================================================
# CART SIGNALS
# =========================================================
@receiver(
    post_save,
    sender=CartItem,
)
def cart_item_post_save(
    sender,
    instance: CartItem,
    created: bool,
    **kwargs,
) -> None:
    """
    Handle cart item events.
    """

    def log_cart_event() -> None:

        if created:

            logger.info(
                (
                    "Cart item added | "
                    "User=%s | "
                    "Product=%s | "
                    "Quantity=%s"
                ),
                instance.user_id,
                instance.product_id,
                instance.qty,
            )

            return

        logger.info(
            (
                "Cart item updated | "
                "User=%s | "
                "Product=%s | "
                "Quantity=%s"
            ),
            instance.user_id,
            instance.product_id,
            instance.qty,
        )

    transaction.on_commit(
        log_cart_event
    )


@receiver(
    post_delete,
    sender=CartItem,
)
def cart_item_post_delete(
    sender,
    instance: CartItem,
    **kwargs,
) -> None:
    """
    Handle cart item deletion.
    """

    transaction.on_commit(
        lambda: logger.info(
            (
                "Cart item removed | "
                "User=%s | "
                "Product=%s"
            ),
            instance.user_id,
            instance.product_id,
        )
    )


# =========================================================
# WISHLIST SIGNALS
# =========================================================
@receiver(
    post_save,
    sender=WishlistItem,
)
def wishlist_item_post_save(
    sender,
    instance: WishlistItem,
    created: bool,
    **kwargs,
) -> None:
    """
    Handle wishlist events.
    """

    if not created:
        return

    transaction.on_commit(
        lambda: logger.info(
            (
                "Wishlist item added | "
                "User=%s | "
                "Product=%s"
            ),
            instance.user_id,
            instance.product_id,
        )
    )


@receiver(
    post_delete,
    sender=WishlistItem,
)
def wishlist_item_post_delete(
    sender,
    instance: WishlistItem,
    **kwargs,
) -> None:
    """
    Handle wishlist deletion.
    """

    transaction.on_commit(
        lambda: logger.info(
            (
                "Wishlist item removed | "
                "User=%s | "
                "Product=%s"
            ),
            instance.user_id,
            instance.product_id,
        )
    )