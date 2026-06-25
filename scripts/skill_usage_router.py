#!/usr/bin/env python3
"""Deterministic, report-only skill-usage router (SPEC-SKILL-USAGE-ROUTER-001).

Answers "which skills should this scenario use?" from a static, tracked TOML table
(``config/agent-control/skill-scenarios.toml``) — replacing per-turn human/LLM memory
with a deterministic lookup. Pure function of its inputs and the table; performs no
network or LLM call (R1, R6/AC6). Advisory / report-only: an unknown or unmatched
scenario yields an empty advisory and never raises for "no match" (R5).

Public API:
    load_table(path=None) -> dict[str, ScenarioEntry-like dict]
    suggest(*, scenario=None, role=None, changed_paths=None, bridge_status=None,
            bridge_kind=None, target_files=None, report_type=None, table=None)
        -> SkillSuggestion

Source: WI-4810 router slice; umbrella ``DELIB-20265883``; owner grilling
``DELIB-20265895``; advisory ``INSIGHTS-2026-05-15-14-35-skill-usage-advisory``.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# scripts/ -> project root (E:\GT-KB). Matches the resolution other scripts use.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TABLE_PATH = _PROJECT_ROOT / "config" / "agent-control" / "skill-scenarios.toml"

# The six scenarios the initial table must define (SPEC R3). Used only for
# diagnostics/validation messaging; the table file is the authoritative source.
EXPECTED_SCENARIOS = (
    "lo_bridge_review",
    "lo_verify_report",
    "advisory_report",
    "harness_surface_change",
    "session_wrap",
    "release_readiness",
)

# Substrings that identify a harness-surface change (R4 signal matching). Conservative:
# only paths that clearly touch a harness/hook/role/adapter/startup/skill/MCP/plugin
# surface match. Substring match against the POSIX form of each changed path.
_HARNESS_SURFACE_MARKERS = (
    ".claude/",
    ".codex/",
    ".cursor/",
    ".agent/",
    "/hooks/",
    "hooks.json",
    "settings.json",
    "harness-",
    "/skills/",
    "session_self_initialization",
    "adapter",
    "/mcp",
    "mcp_",
    "plugin",
)


class SkillRouterError(RuntimeError):
    """Raised on a genuine table load/validation failure (not on a no-match)."""


@dataclass(frozen=True)
class SkillSuggestion:
    """Result of a router query. Report-only; empty when no scenario matched."""

    scenario: str | None
    required: list[str] = field(default_factory=list)
    recommended: list[str] = field(default_factory=list)
    rationale: str = ""
    matched_by: str | None = None

    @property
    def is_empty(self) -> bool:
        return self.scenario is None

    def as_dict(self) -> dict[str, Any]:
        return {
            "scenario": self.scenario,
            "required": list(self.required),
            "recommended": list(self.recommended),
            "rationale": self.rationale,
            "matched_by": self.matched_by,
        }


def load_table(path: Path | str | None = None) -> dict[str, dict[str, Any]]:
    """Load and validate the scenario table.

    Raises ``SkillRouterError`` if the file is missing or any scenario row lacks
    ``required`` (list) / ``recommended`` (list) / ``rationale`` (str). Returns a
    mapping of scenario key -> {title, required, recommended, rationale}.
    """
    table_path = Path(path) if path is not None else DEFAULT_TABLE_PATH
    try:
        raw = tomllib.loads(table_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SkillRouterError(f"skill-scenarios table not found: {table_path}") from exc
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise SkillRouterError(f"skill-scenarios table unreadable: {table_path}: {exc}") from exc

    scenarios = raw.get("scenarios")
    if not isinstance(scenarios, dict) or not scenarios:
        raise SkillRouterError(f"skill-scenarios table has no [scenarios.*] tables: {table_path}")

    out: dict[str, dict[str, Any]] = {}
    for key, entry in scenarios.items():
        if not isinstance(entry, dict):
            raise SkillRouterError(f"scenario {key!r} is not a table")
        required = entry.get("required")
        recommended = entry.get("recommended")
        rationale = entry.get("rationale")
        if not isinstance(required, list) or not all(isinstance(s, str) for s in required):
            raise SkillRouterError(f"scenario {key!r} 'required' must be a list of strings")
        if not isinstance(recommended, list) or not all(isinstance(s, str) for s in recommended):
            raise SkillRouterError(f"scenario {key!r} 'recommended' must be a list of strings")
        if not isinstance(rationale, str) or not rationale.strip():
            raise SkillRouterError(f"scenario {key!r} 'rationale' must be a non-empty string")
        out[key] = {
            "title": entry.get("title", key),
            "required": list(required),
            "recommended": list(recommended),
            "rationale": rationale,
        }
    return out


def _normalize_paths(values: list[str] | tuple[str, ...] | None) -> list[str]:
    if not values:
        return []
    return [str(v).replace("\\", "/") for v in values]


def _match_scenario(
    *,
    role: str | None,
    changed_paths: list[str],
    bridge_status: str | None,
    bridge_kind: str | None,
    target_files: list[str],
    report_type: str | None,
    table: dict[str, dict[str, Any]],
) -> tuple[str | None, str | None]:
    """Deterministic, conservative signal->scenario matcher (SPEC R4).

    Returns (scenario_key, matched_by) or (None, None). Only returns a key that
    exists in the table. Order encodes priority; the first clear signal wins.
    """
    status = (bridge_status or "").strip().upper()
    kind = (bridge_kind or "").strip().lower()
    report = (report_type or "").strip().lower()

    def pick(key: str, signal: str) -> tuple[str | None, str | None]:
        return (key, signal) if key in table else (None, None)

    # 1. A post-implementation report under review -> verify.
    if kind in {"implementation_report", "implementation_verification"}:
        return pick("lo_verify_report", "bridge_kind")
    # 2. An advisory bridge entry / advisory report request.
    if kind in {"loyal_opposition_advisory", "advisory"} or report == "advisory":
        return pick("advisory_report", "bridge_kind" if kind else "report_type")
    # 3. Explicit report-type signals.
    if report in {"session_wrap", "wrap", "wrapup", "wrap_up"}:
        return pick("session_wrap", "report_type")
    if report in {"release", "release_readiness", "deploy", "deployment"}:
        return pick("release_readiness", "report_type")
    # 4. A NEW/REVISED proposal under review.
    if status in {"NEW", "REVISED"}:
        return pick("lo_bridge_review", "bridge_status")
    # 5. A harness-surface change in the changed/target paths.
    candidates = changed_paths + target_files
    if candidates and any(marker in path.lower() for path in candidates for marker in _HARNESS_SURFACE_MARKERS):
        return pick("harness_surface_change", "changed_paths")
    # 6. No clear signal -> no match (report-only, empty advisory).
    return (None, None)


def suggest(
    *,
    scenario: str | None = None,
    role: str | None = None,
    changed_paths: list[str] | tuple[str, ...] | None = None,
    bridge_status: str | None = None,
    bridge_kind: str | None = None,
    target_files: list[str] | tuple[str, ...] | None = None,
    report_type: str | None = None,
    table: dict[str, dict[str, Any]] | None = None,
) -> SkillSuggestion:
    """Return a skill suggestion for the given signals (SPEC R1/R4/R5).

    An explicit ``scenario`` selects directly. Otherwise a deterministic signal
    matcher maps the available inputs to at most one scenario. An unknown explicit
    scenario or no match yields an empty advisory (``scenario is None``); this
    function never raises for "no match" (R5). It MAY raise ``SkillRouterError`` only
    when it must load the default table and that load/validation fails.
    """
    if table is None:
        table = load_table()

    matched_by: str | None
    key: str | None
    if scenario is not None:
        key = scenario if scenario in table else None
        matched_by = "scenario" if key is not None else None
    else:
        key, matched_by = _match_scenario(
            role=role,
            changed_paths=_normalize_paths(changed_paths),
            bridge_status=bridge_status,
            bridge_kind=bridge_kind,
            target_files=_normalize_paths(target_files),
            report_type=report_type,
            table=table,
        )

    if key is None:
        return SkillSuggestion(scenario=None)

    entry = table[key]
    return SkillSuggestion(
        scenario=key,
        required=list(entry["required"]),
        recommended=list(entry["recommended"]),
        rationale=str(entry["rationale"]),
        matched_by=matched_by,
    )
