"""
GroundTruth KB — Pluggable Governance Gates.

Gates are enforcement hooks that run at spec/work-item lifecycle transitions.
The core ships with two built-in gates (ADR/DCL assertion enforcement and
owner-approval for defect/regression WI resolution). Downstream projects
can register additional gates via the ``governance_gates`` config list.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import importlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class GovernanceGateError(ValueError):
    """Raised when a governance gate blocks a transition."""


class GovernanceGate(ABC):
    """Abstract base class for governance gates.

    Subclass and implement the hooks you need. Hooks that return without
    raising are treated as passing.
    """

    @abstractmethod
    def name(self) -> str:
        """Human-readable gate name for error messages."""

    def pre_promote(  # noqa: B027
        self, spec_id: str, current_status: str, target_status: str, spec_data: dict[str, Any]
    ) -> None:
        """Called before a spec status promotion (e.g. specified → implemented).

        Raise GovernanceGateError to block the promotion.
        Override in subclasses — intentionally not abstract so gates can implement only the hooks they need.
        """

    def pre_resolve_work_item(  # noqa: B027
        self, wi_id: str, origin: str, resolution: str, owner_approved: bool, wi_data: dict[str, Any]
    ) -> None:
        """Called before a work item is resolved.

        Raise GovernanceGateError to block the resolution.
        Override in subclasses — intentionally not abstract so gates can implement only the hooks they need.
        """

    def pre_test_pass(  # noqa: B027
        self,
        test_id: str,
        spec_id: str,
        test_file: str | None,
        test_data: dict[str, Any],
    ) -> None:
        """Called before a test is marked as 'pass'.

        Raise GovernanceGateError to block the test pass.
        Override in subclasses — intentionally not abstract so gates can implement only the hooks they need.
        """


class ADRDCLAssertionGate(GovernanceGate):
    """Built-in gate: ADR/DCL specs require non-empty assertions for 'implemented' status."""

    def name(self) -> str:
        return "ADR/DCL Assertion Enforcement"

    def pre_promote(self, spec_id: str, current_status: str, target_status: str, spec_data: dict[str, Any]) -> None:
        if target_status != "implemented":
            return
        spec_type = spec_data.get("type", "")
        if spec_type not in ("architecture_decision", "design_constraint"):
            return
        assertions = spec_data.get("assertions", "")
        if not assertions or assertions.strip() == "":
            raise GovernanceGateError(
                f"Gate '{self.name()}': {spec_id} (type={spec_type}) requires non-empty "
                f"assertions field before promotion to 'implemented'."
            )


class OwnerApprovalGate(GovernanceGate):
    """Built-in gate: defect/regression WI resolution requires owner approval."""

    def name(self) -> str:
        return "Owner Approval for Defect/Regression"

    def pre_resolve_work_item(
        self, wi_id: str, origin: str, resolution: str, owner_approved: bool, wi_data: dict[str, Any]
    ) -> None:
        if origin not in ("defect", "regression"):
            return
        if resolution != "resolved":
            return
        if not owner_approved:
            raise GovernanceGateError(
                f"Gate '{self.name()}': {wi_id} (origin={origin}) requires owner_approved=True "
                f"before resolution. Set owner_approved=True after owner confirms."
            )


@dataclass
class GateRegistry:
    """Registry of governance gates. Runs all registered gates at lifecycle transitions."""

    _gates: list[GovernanceGate] = field(default_factory=list)

    def register(self, gate: GovernanceGate) -> None:
        self._gates.append(gate)

    def run_pre_promote(self, spec_id: str, current_status: str, target_status: str, spec_data: dict[str, Any]) -> None:
        for gate in self._gates:
            gate.pre_promote(spec_id, current_status, target_status, spec_data)

    def run_pre_resolve_work_item(
        self, wi_id: str, origin: str, resolution: str, owner_approved: bool, wi_data: dict[str, Any]
    ) -> None:
        for gate in self._gates:
            gate.pre_resolve_work_item(wi_id, wi_id, resolution, owner_approved, wi_data)

    def run_pre_test_pass(self, test_id: str, spec_id: str, test_file: str | None, test_data: dict[str, Any]) -> None:
        """Run all registered gates' pre_test_pass hooks."""
        for gate in self._gates:
            gate.pre_test_pass(test_id, spec_id, test_file, test_data)

    @classmethod
    def from_config(
        cls,
        gate_paths: list[str],
        include_builtins: bool = True,
        gate_config: dict[str, dict[str, Any]] | None = None,
        project_root: Path | None = None,
    ) -> GateRegistry:
        """Create a registry from dotted-path strings + optional built-in gates.

        Args:
            gate_paths: List of dotted import paths like "my_module:MyGate".
            include_builtins: If True, register ADRDCLAssertionGate and OwnerApprovalGate.
            gate_config: Optional per-gate config dicts keyed by class name. If a gate's
                         class name appears here and the class has a ``from_config`` classmethod,
                         it will be used instead of the no-arg constructor.
            project_root: Fallback project root injected into gate configs that don't
                          specify their own. Ensures file-resolution gates use the
                          project root from GTConfig, not cwd.
        """
        gate_config = gate_config or {}
        registry = cls()
        if include_builtins:
            registry.register(ADRDCLAssertionGate())
            registry.register(OwnerApprovalGate())
        for path in gate_paths:
            gate_cls = _import_gate(path)
            cfg = dict(gate_config.get(gate_cls.__name__, {}))
            # Inject project_root fallback for gates that need it
            if project_root is not None and "project_root" not in cfg:
                cfg["project_root"] = str(project_root)
            if cfg and hasattr(gate_cls, "from_config"):
                registry.register(gate_cls.from_config(cfg))
            else:
                registry.register(gate_cls())
        return registry


def _import_gate(dotted_path: str) -> type[GovernanceGate]:
    """Import a GovernanceGate subclass from a dotted path like 'module.submodule:ClassName'."""
    if ":" not in dotted_path:
        raise ValueError(f"Gate path must be 'module:ClassName', got: {dotted_path!r}")
    module_path, class_name = dotted_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    if not (isinstance(cls, type) and issubclass(cls, GovernanceGate)):
        raise TypeError(f"{dotted_path} is not a GovernanceGate subclass")
    return cls
