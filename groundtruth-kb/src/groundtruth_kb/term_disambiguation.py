# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Shared library for canonical-terminology disambiguation enforcement.

Per GTKB-GOV-TERM-DISAMBIGUATION-MECHANICAL Slice 1 (S327, bridge -006 GO).
This module ships the API surface + policy-loading path; Slice 2 wires this
into the PreToolUse hook (`term-disambiguation-precheck.py`) and Slice 3 wires
this into the PostToolUse audit hook (`term-disambiguation-audit.py`).

The Tier A/B/C lint behavior stubs return empty lists in Slice 1; full
implementation lands in Slices 2-3 per the scoping proposal sequencing
(`bridge/gtkb-gov-term-disambiguation-mechanical-2026-05-02-005.md`).
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

Tier = Literal["A", "B", "C"]
Severity = Literal["error", "warn"]


@dataclass(frozen=True)
class Violation:
    """A single disambiguation violation detected in scanned content.

    Slice 1: API surface only. Tier-specific detection lands in Slices 2-3.

    Attributes:
        term: The canonical term involved (e.g., ``"backlog"``).
        tier: ``"A"`` (distinctive form), ``"B"`` (capitalization), or
            ``"C"`` (specific instance reference).
        severity: ``"error"`` (PreToolUse-blockable) or ``"warn"``
            (PostToolUse audit-only).
        line: 1-indexed line number where the violation was detected.
        message: Human-readable description of the violation.
        suggestion: Suggested replacement or qualification (may be empty).
    """

    term: str
    tier: Tier
    severity: Severity
    line: int
    message: str
    suggestion: str = ""


@dataclass(frozen=True)
class PolicyConfig:
    """Loaded view of `canonical-terminology-policy.toml`.

    The default factory loads from the GT-KB-installed path
    (`.claude/rules/canonical-terminology-policy.toml`) at the project
    root. Tests pass an explicit path.
    """

    defaults: dict[str, Any] = field(default_factory=dict)
    terms: dict[str, dict[str, Any]] = field(default_factory=dict)

    @classmethod
    def load(cls, policy_path: Path) -> PolicyConfig:
        """Load and return a `PolicyConfig` from a TOML file.

        Raises:
            FileNotFoundError: when ``policy_path`` does not exist.
            tomllib.TOMLDecodeError: when the file is not valid TOML.
        """
        data = tomllib.loads(policy_path.read_text(encoding="utf-8"))
        defaults_section = data.get("defaults", {})
        terms_section = data.get("term", {})
        if not isinstance(defaults_section, dict):
            defaults_section = {}
        if not isinstance(terms_section, dict):
            terms_section = {}
        return cls(
            defaults=dict(defaults_section),
            terms={k: dict(v) for k, v in terms_section.items() if isinstance(v, dict)},
        )


def evaluate_content(
    content: str,
    *,
    file_path: Path,
    policy: PolicyConfig,
) -> list[Violation]:
    """Evaluate `content` against the disambiguation policy.

    Slice 1 ships the API surface + file-level-disable-marker honoring.
    Tier A/B/C lint logic is implemented in Slice 2 (PreToolUse deny path
    for ``error`` severities) and Slice 3 (PostToolUse audit for ``warn``).

    Args:
        content: The full text content to evaluate.
        file_path: The target file path (used for context-sensitive
            decisions in Slices 2-3, e.g., bridge-proposal escalation).
        policy: Loaded `PolicyConfig`.

    Returns:
        List of `Violation` instances. Empty list = no violations
        detected (or file is exempt via the file-level disable marker).
    """
    violations: list[Violation] = []

    # File-level disable marker honors per pinned default §G.
    disable_marker = policy.defaults.get("file_level_disable_marker", "")
    if disable_marker and disable_marker in content:
        return violations

    # Tier A / Tier B / Tier C / forbidden-uses scanning logic lands in
    # Slices 2-3. Slice 1 returns no violations to keep the API contract
    # callable from the upcoming hooks without behavioral side effects.
    _ = file_path

    return violations


__all__ = ["Tier", "Severity", "Violation", "PolicyConfig", "evaluate_content"]
