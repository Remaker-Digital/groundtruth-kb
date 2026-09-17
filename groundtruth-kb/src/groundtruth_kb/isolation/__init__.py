from .app_root_minimization import AppRootMinimizationResult, validate_app_root_minimization
from .doctor_verdicts import evaluate_isolation_state
from .occupancy_detector import detect_occupancy
from .registry_check import has_registry_entry
from .validation import ValidationError, check_slot_markers, validate_self_completion_preflight

__all__ = [
    "AppRootMinimizationResult",
    "validate_app_root_minimization",
    "has_registry_entry",
    "detect_occupancy",
    "evaluate_isolation_state",
    "check_slot_markers",
    "ValidationError",
    "validate_self_completion_preflight",
]
