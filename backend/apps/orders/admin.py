from __future__ import annotations

import importlib
import logging
import pkgutil

from apps.orders import (
    admin_views,
)


logger = logging.getLogger(
    __name__
)


# =========================================================
# AUTO DISCOVER ADMIN MODULES
# =========================================================
EXCLUDED_MODULES = {
    "base",
    "mixins",
    "__pycache__",
}


for module_info in pkgutil.iter_modules(
    admin_views.__path__,
):

    module_name = (
        module_info.name
    )

    # SKIP PACKAGES
    if module_info.ispkg:
        continue

    # SKIP PRIVATE/UTILITY MODULES
    if (
        module_name.startswith("_")
        or module_name
        in EXCLUDED_MODULES
    ):
        logger.debug(
            (
                "Skipping admin module: %s"
            ),
            module_name,
        )

        continue

    full_module_path = (
        f"{admin_views.__name__}."
        f"{module_name}"
    )

    try:
        importlib.import_module(
            full_module_path,
        )

        logger.info(
            (
                "Successfully imported "
                "admin module: %s"
            ),
            full_module_path,
        )

    except Exception:
        logger.exception(
            (
                "Failed to import "
                "admin module: %s"
            ),
            full_module_path,
        )

        # CONTINUE LOADING
        # OTHER ADMIN MODULES
        continue