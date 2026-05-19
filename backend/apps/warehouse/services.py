from __future__ import annotations

import logging
from decimal import Decimal
from typing import Iterable

from django.db import transaction
from django.db.models import (
    F,
    QuerySet,
)

from .models import Warehouse


logger = logging.getLogger(
    __name__
)


# =========================================================
# WAREHOUSE ALLOCATION SERVICE
# =========================================================
class WarehouseAllocationService:
    """
    Intelligent warehouse allocation service.

    Features:
    - Active warehouse filtering
    - Default warehouse prioritization
    - Capacity-aware allocation
    - City-based prioritization
    - Load balancing support
    - Transaction-safe allocation
    """

    # =====================================================
    # ALLOCATE WAREHOUSE
    # =====================================================
    @classmethod
    @transaction.atomic
    def allocate(
        cls,
        order,
        warehouses: QuerySet[Warehouse],
    ) -> Warehouse | None:
        """
        Allocate best warehouse for order.

        Returns:
            Warehouse | None
        """

        if not warehouses.exists():

            logger.warning(
                (
                    "Warehouse allocation failed | "
                    "No warehouses available."
                )
            )

            return None

        # =================================================
        # FILTER ACTIVE WAREHOUSES
        # =================================================
        candidate_warehouses = (
            warehouses.select_for_update()
            .filter(
                status=Warehouse.Status.ACTIVE,
            )
        )

        if not candidate_warehouses.exists():

            logger.warning(
                (
                    "Warehouse allocation failed | "
                    "No active warehouses."
                )
            )

            return None

        # =================================================
        # FILTER AVAILABLE CAPACITY
        # =================================================
        candidate_warehouses = (
            candidate_warehouses.filter(
                capacity__gt=F(
                    "current_stock"
                )
            )
        )

        if not candidate_warehouses.exists():

            logger.warning(
                (
                    "Warehouse allocation failed | "
                    "No warehouse has "
                    "available capacity."
                )
            )

            return None

        # =================================================
        # PRIORITIZE SAME CITY
        # =================================================
        shipping_city = (
            cls._get_shipping_city(
                order
            )
        )

        if shipping_city:

            city_warehouses = (
                candidate_warehouses.filter(
                    city__iexact=shipping_city
                )
            )

            if city_warehouses.exists():

                logger.info(
                    (
                        "City-based warehouse "
                        "allocation applied | "
                        "City=%s"
                    ),
                    shipping_city,
                )

                candidate_warehouses = (
                    city_warehouses
                )

        # =================================================
        # PRIORITIZE DEFAULT WAREHOUSE
        # =================================================
        default_warehouse = (
            candidate_warehouses.filter(
                is_default=True
            )
            .order_by("name")
            .first()
        )

        if default_warehouse:

            logger.info(
                (
                    "Default warehouse "
                    "allocated | "
                    "Warehouse=%s"
                ),
                default_warehouse.name,
            )

            return default_warehouse

        # =================================================
        # LOAD BALANCING STRATEGY
        # =================================================
        best_warehouse = (
            candidate_warehouses.order_by(
                "current_stock",
                "-capacity",
                "name",
            ).first()
        )

        if not best_warehouse:

            logger.warning(
                (
                    "Warehouse allocation failed | "
                    "No suitable warehouse found."
                )
            )

            return None

        logger.info(
            (
                "Warehouse allocated successfully | "
                "Warehouse=%s | "
                "Code=%s"
            ),
            best_warehouse.name,
            best_warehouse.code,
        )

        return best_warehouse

    # =====================================================
    # GET SHIPPING CITY
    # =====================================================
    @staticmethod
    def _get_shipping_city(
        order,
    ) -> str | None:
        """
        Extract shipping city from order.
        """

        shipping_address = getattr(
            order,
            "shipping_address",
            None,
        )

        if not shipping_address:

            return None

        city = getattr(
            shipping_address,
            "city",
            None,
        )

        if not city:

            return None

        return city.strip()

    # =====================================================
    # GET ELIGIBLE WAREHOUSES
    # =====================================================
    @classmethod
    def get_eligible_warehouses(
        cls,
        warehouses: QuerySet[Warehouse],
    ) -> QuerySet[Warehouse]:
        """
        Return only active warehouses
        with available capacity.
        """

        return (
            warehouses.filter(
                status=Warehouse.Status.ACTIVE,
                capacity__gt=F(
                    "current_stock"
                ),
            )
            .order_by(
                "name"
            )
        )

    # =====================================================
    # CHECK CAPACITY
    # =====================================================
    @staticmethod
    def has_available_capacity(
        warehouse: Warehouse,
    ) -> bool:
        """
        Check warehouse capacity.
        """

        return bool(
            warehouse.capacity
            > warehouse.current_stock
        )

    # =====================================================
    # RESERVE STOCK SLOT
    # =====================================================
    @classmethod
    @transaction.atomic
    def reserve_capacity(
        cls,
        warehouse: Warehouse,
        quantity: int = 1,
    ) -> bool:
        """
        Reserve warehouse capacity.
        """

        refreshed_warehouse = (
            Warehouse.objects.select_for_update()
            .filter(
                pk=warehouse.pk,
            )
            .first()
        )

        if not refreshed_warehouse:

            logger.warning(
                (
                    "Warehouse not found "
                    "during reservation."
                )
            )

            return False

        available_capacity = (
            refreshed_warehouse.available_capacity
        )

        if quantity > available_capacity:

            logger.warning(
                (
                    "Warehouse reservation failed | "
                    "Insufficient capacity."
                )
            )

            return False

        refreshed_warehouse.current_stock += (
            quantity
        )

        refreshed_warehouse.save(
            update_fields=[
                "current_stock",
                "updated_at",
            ]
        )

        logger.info(
            (
                "Warehouse capacity reserved | "
                "Warehouse=%s | "
                "Quantity=%s"
            ),
            refreshed_warehouse.name,
            quantity,
        )

        return True

    # =====================================================
    # RELEASE CAPACITY
    # =====================================================
    @classmethod
    @transaction.atomic
    def release_capacity(
        cls,
        warehouse: Warehouse,
        quantity: int = 1,
    ) -> bool:
        """
        Release reserved warehouse capacity.
        """

        refreshed_warehouse = (
            Warehouse.objects.select_for_update()
            .filter(
                pk=warehouse.pk,
            )
            .first()
        )

        if not refreshed_warehouse:

            logger.warning(
                (
                    "Warehouse not found "
                    "during release."
                )
            )

            return False

        refreshed_warehouse.current_stock = max(
            refreshed_warehouse.current_stock
            - quantity,
            0,
        )

        refreshed_warehouse.save(
            update_fields=[
                "current_stock",
                "updated_at",
            ]
        )

        logger.info(
            (
                "Warehouse capacity released | "
                "Warehouse=%s | "
                "Quantity=%s"
            ),
            refreshed_warehouse.name,
            quantity,
        )

        return True