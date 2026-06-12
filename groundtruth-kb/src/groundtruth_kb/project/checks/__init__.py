# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Registry for dynamically discovered doctor checks (ADR-REGISTRY-DISCOVERY-001)."""

from __future__ import annotations

import importlib
import pkgutil
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from groundtruth_kb.project.doctor import ToolCheck

CheckFunc = Callable[[Path], "ToolCheck"]

_REGISTRY: dict[str, CheckFunc] = {}


def register_check(name: str) -> Callable[[CheckFunc], CheckFunc]:
    """Decorator to register a doctor check function."""

    def decorator(func: CheckFunc) -> CheckFunc:
        _REGISTRY[name] = func
        return func

    return decorator


def get_registered_checks() -> dict[str, CheckFunc]:
    """Load all modules in the checks directory and return the registry."""
    package_name = __name__
    package = importlib.import_module(package_name)
    package_path = package.__path__ if hasattr(package, "__path__") else None
    if package_path:
        for _, module_name, _ in pkgutil.iter_modules(package_path):
            importlib.import_module(f"{package_name}.{module_name}")
    return _REGISTRY
