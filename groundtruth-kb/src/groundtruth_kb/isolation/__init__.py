from .allowlist import is_allowlisted_file
from .app_root_minimization import AppRootMinimizationResult, validate_app_root_minimization
from .doctor_verdicts import check_slot_markers, evaluate_isolation_state
from .occupancy_detector import detect_occupancy
from .registry_check import has_registry_entry
from .strong_markers import has_strong_marker
from .validation import ValidationError, validate_self_completion_preflight

__all__ = [
    "is_allowlisted_file",
    "AppRootMinimizationResult",
    "validate_app_root_minimization",
    "has_strong_marker",
    "has_registry_entry",
    "detect_occupancy",
    "evaluate_isolation_state",
    "check_slot_markers",
    "ValidationError",
    "validate_self_completion_preflight",
]
