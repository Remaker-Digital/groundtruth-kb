#!/usr/bin/env python3
"""Canonical Skills-applied self-disclosure emitter/parser (SPEC-REPORT-SKILL-DISCLOSURE-001).

Deterministic, report-only helpers shared across bridge verdicts, LO reports, and session
wraps. No network or LLM calls.
"""

from __future__ import annotations

SKILLS_APPLIED_PREFIX = "Skills applied:"


def format_skills_applied(skills: list[str]) -> str:
    """Return the canonical disclosure line for *skills* (de-duplicated, order-preserving)."""
    seen: set[str] = set()
    ordered: list[str] = []
    for raw in skills:
        name = str(raw).strip()
        if not name or name in seen:
            continue
        seen.add(name)
        ordered.append(name)
    if not ordered:
        return f"{SKILLS_APPLIED_PREFIX} (none)"
    return f"{SKILLS_APPLIED_PREFIX} " + ", ".join(ordered)


def parse_skills_applied(text: str) -> list[str]:
    """Extract skill names from *text*; missing line -> empty list (no error)."""
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.lower().startswith(SKILLS_APPLIED_PREFIX.lower()):
            continue
        payload = stripped.split(":", 1)[1].strip()
        if not payload or payload == "(none)":
            return []
        return [part.strip() for part in payload.split(",") if part.strip()]
    return []
