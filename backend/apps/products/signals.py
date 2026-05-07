# backend/apps/products/signals.py

"""
Signals for the Products app.

This module is automatically loaded from:
    apps.products.apps.ProductsConfig.ready()

Use this file for:
- Product lifecycle hooks
- Cart/Wishlist signals
- Inventory updates
- Search indexing
- Analytics triggers
- Admin notifications
"""

import logging

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from .models import (
    Product,
    CartItem,
    WishlistItem,
)

logger = logging.getLogger(__name__)


# =========================================================
# PRODUCT SIGNALS
# =========================================================

@receiver(pre_save, sender=Product)
def store_old_product_state(sender, instance, **kwargs):
    """
    Store previous product state before update.

    Useful for:
    - inventory tracking
    - price change logs
    - audit/history systems
    """

    if not instance.pk:
        instance._old_instance = None
        return

    old_instance = (
        Product.objects
        .filter(pk=instance.pk)
        .first()
    )

    instance._old_instance = old_instance


@receiver(post_save, sender=Product)
def product_post_save(sender, instance, created, **kwargs):
    """
    Handle product create/update events.
    """

    if created:
        logger.info(
            "New product created | ID=%s | Name=%s",
            instance.id,
            instance.name,
        )

        # Future:
        # - Send admin notification
        # - Index into search engine
        # - Generate AI metadata
        # - Trigger cache refresh

        return

    old_instance = getattr(instance, "_old_instance", None)

    if not old_instance:
        return

    # -----------------------------------------------------
    # PRICE CHANGED
    # -----------------------------------------------------
    if old_instance.price != instance.price:
        logger.info(
            "Product price updated | Product=%s | Old=%s | New=%s",
            instance.name,
            old_instance.price,
            instance.price,
        )

    # -----------------------------------------------------
    # STOCK CHANGED
    # -----------------------------------------------------
    old_stock = getattr(old_instance, "stock", None)
    new_stock = getattr(instance, "stock", None)

    if old_stock != new_stock:
        logger.info(
            "Product stock updated | Product=%s | Old=%s | New=%s",
            instance.name,
            old_stock,
            new_stock,
        )

        # Example future logic:
        #
        # if new_stock == 0:
        #     send_out_of_stock_notification(instance)


@receiver(post_delete, sender=Product)
def product_post_delete(sender, instance, **kwargs):
    """
    Handle product deletion cleanup.
    """

    logger.warning(
        "Product deleted | ID=%s | Name=%s",
        instance.id,
        instance.name,
    )

    # Future:
    # - Remove search indexes
    # - Delete cache
    # - Remove CDN assets
    # - Archive analytics


# =========================================================
# CART SIGNALS
# =========================================================

@receiver(post_save, sender=CartItem)
def cart_item_post_save(sender, instance, created, **kwargs):
    """
    Handle cart item create/update.
    """

    if created:
        logger.info(
            "Cart item added | User=%s | Product=%s | Quantity=%s",
            instance.user,
            instance.product,
            instance.quantity,
        )
        return

    logger.info(
        "Cart item updated | User=%s | Product=%s | Quantity=%s",
        instance.user,
        instance.product,
        instance.quantity,
    )


@receiver(post_delete, sender=CartItem)
def cart_item_post_delete(sender, instance, **kwargs):
    """
    Handle cart item removal.
    """

    logger.info(
        "Cart item removed | User=%s | Product=%s",
        instance.user,
        instance.product,
    )


# =========================================================
# WISHLIST SIGNALS
# =========================================================

@receiver(post_save, sender=WishlistItem)
def wishlist_item_post_save(sender, instance, created, **kwargs):
    """
    Handle wishlist item creation.
    """

    if created:
        logger.info(
            "Wishlist item added | User=%s | Product=%s",
            instance.user,
            instance.product,
        )


@receiver(post_delete, sender=WishlistItem)
def wishlist_item_post_delete(sender, instance, **kwargs):
    """
    Handle wishlist item deletion.
    """

    logger.info(
        "Wishlist item removed | User=%s | Product=%s",
        instance.user,
        instance.product,
    )