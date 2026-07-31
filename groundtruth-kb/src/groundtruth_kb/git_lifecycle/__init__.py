"""Deterministic, observable, and recoverable GT-KB Git lifecycle service."""

from groundtruth_kb.git_lifecycle.commands import CommandBoundary, CommandResult, SubprocessCommandBoundary
from groundtruth_kb.git_lifecycle.models import OperationDenied, OperationResult, PromotionEvidence
from groundtruth_kb.git_lifecycle.quiescence import (
    MAX_QUIESCENCE_TTL_SECONDS,
    acquire_dispatcher_quiescence,
    recover_dispatcher_quiescence,
    verify_dispatcher_quiescence,
)
from groundtruth_kb.git_lifecycle.service import GitLifecycleService, deterministic_work_branch

__all__ = [
    "MAX_QUIESCENCE_TTL_SECONDS",
    "CommandBoundary",
    "CommandResult",
    "GitLifecycleService",
    "OperationDenied",
    "OperationResult",
    "PromotionEvidence",
    "SubprocessCommandBoundary",
    "acquire_dispatcher_quiescence",
    "deterministic_work_branch",
    "recover_dispatcher_quiescence",
    "verify_dispatcher_quiescence",
]
