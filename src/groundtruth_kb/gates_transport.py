"""
GroundTruth KB — Transport Evidence Governance Gate.

Plugin gate for projects that require executable test evidence before
transport/container specs can be promoted to 'verified' or their tests
marked as 'pass'. Originally built for Agent Red's transport recovery
pipeline (Phase 0 governance).

Usage in groundtruth.toml::

    [gates]
    plugins = ["groundtruth_kb.gates_transport:TransportEvidenceGate"]

    [gates.config.TransportEvidenceGate]
    spec_ids = ["SPEC-1524", "SPEC-1525", "SPEC-1535", "SPEC-1536", "SPEC-1537", "SPEC-1802"]

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from groundtruth_kb.gates import GovernanceGate, GovernanceGateError


class TransportEvidenceGateError(GovernanceGateError):
    """Raised when a transport/container test or spec promotion lacks executable evidence."""


class TransportEvidenceGate(GovernanceGate):
    """Gate requiring executable test evidence for transport-gated specifications.

    Two enforcement points:
    1. **pre_test_pass**: Blocks marking a test as 'pass' for a gated spec
       unless test_file points to a real file on disk.
    2. **pre_promote**: Blocks promoting a gated spec to 'verified' unless
       all linked tests have test_file (real file) and last_result='pass'.
    """

    def __init__(
        self,
        spec_ids: set[str] | frozenset[str] | None = None,
        project_root: Path | None = None,
    ):
        self._spec_ids: frozenset[str] = frozenset(spec_ids) if spec_ids else frozenset()
        self._project_root: Path = project_root or Path(".")

    def name(self) -> str:
        return "Transport Evidence Gate"

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> TransportEvidenceGate:
        """Create from TOML config dict.

        Expected keys:
            spec_ids: list of spec ID strings
            project_root: path string (optional, defaults to ".")
        """
        spec_ids = set(config.get("spec_ids", []))
        project_root_str = config.get("project_root")
        project_root = Path(project_root_str) if project_root_str else None
        return cls(spec_ids=spec_ids, project_root=project_root)

    def _resolve_test_file(self, test_file: str | None) -> Path | None:
        """Resolve a test_file path against the project root."""
        if not test_file:
            return None
        candidate = self._project_root / test_file
        return candidate if candidate.is_file() else None

    def pre_test_pass(
        self,
        test_id: str,
        spec_id: str,
        test_file: str | None,
        test_data: dict[str, Any],
    ) -> None:
        """Block test 'pass' for transport-gated specs without executable evidence."""
        if spec_id not in self._spec_ids:
            return
        if not test_file:
            raise TransportEvidenceGateError(
                f"Cannot mark test as 'pass' for transport-gated spec {spec_id}: "
                f"test_file is required (must be a real, executable test file path). "
                f"Transport evidence gate — executable evidence required."
            )
        if not self._resolve_test_file(test_file):
            raise TransportEvidenceGateError(
                f"Cannot mark test as 'pass' for transport-gated spec {spec_id}: "
                f"test_file '{test_file}' does not exist on disk. "
                f"Transport evidence gate — executable evidence requires a real file."
            )

    def pre_promote(
        self,
        spec_id: str,
        current_status: str,
        target_status: str,
        spec_data: dict[str, Any],
    ) -> None:
        """Block promotion to 'verified' for transport-gated specs without full evidence."""
        if target_status != "verified":
            return
        if spec_id not in self._spec_ids:
            return

        linked_tests = spec_data.get("linked_tests", [])
        if not linked_tests:
            raise TransportEvidenceGateError(
                f"Cannot promote {spec_id} to 'verified': no linked tests found. "
                f"Transport evidence gate — executable test evidence required."
            )
        for test in linked_tests:
            tid = test.get("id", "?")
            tf = test.get("test_file")
            if not tf:
                raise TransportEvidenceGateError(
                    f"Cannot promote {spec_id} to 'verified': test {tid} "
                    f"has no test_file (no executable evidence). "
                    f"Transport evidence gate."
                )
            if not self._resolve_test_file(tf):
                raise TransportEvidenceGateError(
                    f"Cannot promote {spec_id} to 'verified': test {tid} "
                    f"has test_file='{tf}' which does not exist on disk. "
                    f"Transport evidence gate — executable evidence requires a real file."
                )
            if test.get("last_result") != "pass":
                raise TransportEvidenceGateError(
                    f"Cannot promote {spec_id} to 'verified': test {tid} "
                    f"has last_result='{test.get('last_result')}', not 'pass'. "
                    f"Transport evidence gate."
                )
