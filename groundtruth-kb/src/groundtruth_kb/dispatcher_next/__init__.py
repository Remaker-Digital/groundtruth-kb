"""Isolated durable-workflow foundation for the next-generation dispatcher."""

from __future__ import annotations

from importlib import import_module
from typing import Any

_CAPACITY_EXPORTS = frozenset(
    {
        "CapacityLedger",
        "CapacityLedgerError",
        "CapacityPolicy",
        "CapacityRequest",
        "DuplicateLeaseError",
        "InvalidCapacityPolicy",
        "InvalidCapacityRequest",
    }
)
_FOUNDATION_EXPORTS = frozenset(
    {
        "ADOPT_DBOS_A2A",
        "EXPECTED_A2A_VERSION",
        "EXPECTED_DBOS_VERSION",
        "REJECT_AND_EVALUATE_HATCHET",
        "REQUIRED_PREDICATES",
        "TRANSIENT_RETRY_INTERVAL_SECONDS",
        "TRANSIENT_RETRY_MAX_ATTEMPTS",
        "AdoptionManifest",
        "TransientProbeError",
        "VerificationRecord",
        "dependency_versions",
        "durable_stub_workflow",
        "evaluate_adoption",
        "evaluate_verification_records",
        "recover_workflow",
        "recover_workflow_batch",
        "run_transient_retry_probe",
        "run_workflow_batch",
        "semantic_operation_count",
        "start_crash_once_workflow",
        "start_crash_once_workflow_batch",
        "transient_retry_workflow",
    }
)
_PROTOCOL_EXPORTS = frozenset(
    {
        "A2AProtocolError",
        "A2AProtocolFacade",
        "InvalidTaskTransitionError",
        "LifecycleEvidence",
        "LifecycleResult",
        "TaskAlreadyExistsError",
        "TaskNotFoundError",
        "TerminalOutcome",
        "parse_task",
        "round_trip_task",
        "run_lifecycle",
        "serialize_task",
        "task_to_dict",
    }
)
_EXPORT_MODULES = {
    **{name: "capacity" for name in _CAPACITY_EXPORTS},
    **{name: "foundation" for name in _FOUNDATION_EXPORTS},
    **{name: "protocol" for name in _PROTOCOL_EXPORTS},
}

__all__ = sorted(_EXPORT_MODULES)


def __getattr__(name: str) -> Any:
    """Resolve public exports lazily so ``python -m foundation`` is single-load."""

    module_name = _EXPORT_MODULES.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(f"{__name__}.{module_name}"), name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted({*globals(), *__all__})
