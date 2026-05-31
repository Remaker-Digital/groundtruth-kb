"""Backlog helpers backed by MemBase work_items.

The approval-state slice adds a package namespace below ``groundtruth_kb.backlog``.
Preserve the legacy module-level migration helpers from ``backlog.py`` so
existing imports keep working while new code can import
``groundtruth_kb.backlog.approval_state``.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from groundtruth_kb.backlog.approval_state import (
    ALLOWED_STATES,
    ApprovalState,
    classify_initial_state,
    validate_transition,
)

_LEGACY_MODULE_NAME = "_groundtruth_kb_legacy_backlog"
_LEGACY_MODULE_PATH = Path(__file__).resolve().parents[1] / "backlog.py"

if _LEGACY_MODULE_PATH.exists():
    _spec = importlib.util.spec_from_file_location(_LEGACY_MODULE_NAME, _LEGACY_MODULE_PATH)
    if _spec is not None and _spec.loader is not None:
        _legacy = importlib.util.module_from_spec(_spec)
        sys.modules[_LEGACY_MODULE_NAME] = _legacy
        _spec.loader.exec_module(_legacy)
        for _name in getattr(_legacy, "__all__", None) or dir(_legacy):
            if _name.startswith("_"):
                continue
            globals()[_name] = getattr(_legacy, _name)

__all__ = [
    "ALLOWED_STATES",
    "ApprovalState",
    "classify_initial_state",
    "validate_transition",
]
