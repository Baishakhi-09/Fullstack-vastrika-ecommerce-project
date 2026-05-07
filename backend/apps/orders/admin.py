import importlib
import pkgutil
from . import admin_views

for module_info in pkgutil.iter_modules(admin_views.__path__):
    if not module_info.ispkg:
        try:
            importlib.import_module(f"{admin_views.__name__}.{module_info.name}")
        except Exception as e:
            raise ImportError(
                f"Error importing admin module '{module_info.name}' "
                f"in '{admin_views.__name__}': {e}"
            ) from e