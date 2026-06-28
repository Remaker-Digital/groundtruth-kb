"""Application-scope classification helpers for GT-KB MemBase rows."""

from __future__ import annotations

import re
from dataclasses import dataclass

GTKB_PLATFORM_SCOPE = "gtkb_platform"
AGENT_RED_APPLICATION_SCOPE = "agent_red_application"
VALID_APPLICATION_SCOPES = frozenset({GTKB_PLATFORM_SCOPE, AGENT_RED_APPLICATION_SCOPE})
AGENT_RED_ROOT = "applications/Agent_Red/"

_AGENT_RED_TEXT_RE = re.compile(r"(?:agent[\s_-]?red|agentred)", re.IGNORECASE)
_GENERIC_TOP_LEVEL_PREFIXES = ("scripts/", "tests/", "docs/", "config/", "src/")
_LEGACY_AGENT_RED_PREFIXES = ("Agent_Red/", "agent_red/", "agent-red/")


@dataclass(frozen=True)
class ScopeClassification:
    """Classification result for one spec/test row."""

    proposed_scope: str | None
    normalized_paths: list[str]
    proposed_paths: list[str]
    ambiguous: bool
    reasons: list[str]


def normalize_repo_path(path: str) -> str:
    """Normalize an in-repo path string for classification, not filesystem IO."""
    normalized = path.strip().replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def validate_application_scope(value: str | None) -> str | None:
    """Return a normalized application_scope or raise ValueError."""
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        return None
    if normalized not in VALID_APPLICATION_SCOPES:
        allowed = ", ".join(sorted(VALID_APPLICATION_SCOPES))
        raise ValueError(f"application_scope must be one of: {allowed}")
    return normalized


def is_agent_red_application_path(path: str) -> bool:
    return normalize_repo_path(path).startswith(AGENT_RED_ROOT)


def is_legacy_agent_red_path(path: str) -> bool:
    normalized = normalize_repo_path(path)
    return normalized.startswith(_LEGACY_AGENT_RED_PREFIXES)


def repath_legacy_agent_red_path(path: str) -> str:
    normalized = normalize_repo_path(path)
    for prefix in _LEGACY_AGENT_RED_PREFIXES:
        if normalized.startswith(prefix):
            return AGENT_RED_ROOT + normalized[len(prefix) :]
    return normalized


def has_agent_red_text(*values: str | None) -> bool:
    return any(_AGENT_RED_TEXT_RE.search(value or "") for value in values)


def _is_generic_top_level_path(path: str) -> bool:
    normalized = normalize_repo_path(path)
    return normalized.startswith(_GENERIC_TOP_LEVEL_PREFIXES)


def classify_application_scope(record_id: str, title: str | None, paths: list[str]) -> ScopeClassification:
    """Classify a spec/test row from explicit path evidence.

    Path evidence is intentionally stricter than title text. A title containing
    "Agent Red" is not enough to mutate a row; generic top-level paths stay
    ambiguous until a human review records a precise application path.
    """
    normalized_paths = [normalize_repo_path(path) for path in paths if path and path.strip()]
    proposed_paths = [repath_legacy_agent_red_path(path) for path in normalized_paths]
    reasons: list[str] = []

    if not normalized_paths:
        return ScopeClassification(
            proposed_scope=None,
            normalized_paths=[],
            proposed_paths=[],
            ambiguous=False,
            reasons=["no path evidence"],
        )

    agent_root_paths = [path for path in proposed_paths if is_agent_red_application_path(path)]
    non_agent_paths = [path for path in proposed_paths if not is_agent_red_application_path(path)]
    legacy_agent_paths = [path for path in normalized_paths if is_legacy_agent_red_path(path)]
    text_mentions_agent_red = has_agent_red_text(record_id, title, " ".join(normalized_paths))
    generic_paths = [path for path in normalized_paths if _is_generic_top_level_path(path)]

    if agent_root_paths and not non_agent_paths:
        reasons.append("all path evidence is under applications/Agent_Red/")
        if legacy_agent_paths:
            reasons.append("legacy Agent_Red path evidence repathed to applications/Agent_Red/")
        return ScopeClassification(
            proposed_scope=AGENT_RED_APPLICATION_SCOPE,
            normalized_paths=normalized_paths,
            proposed_paths=proposed_paths,
            ambiguous=False,
            reasons=reasons,
        )

    if agent_root_paths and non_agent_paths:
        return ScopeClassification(
            proposed_scope=None,
            normalized_paths=normalized_paths,
            proposed_paths=proposed_paths,
            ambiguous=True,
            reasons=["mixed application and platform path evidence"],
        )

    if legacy_agent_paths and len(legacy_agent_paths) == len(normalized_paths):
        return ScopeClassification(
            proposed_scope=AGENT_RED_APPLICATION_SCOPE,
            normalized_paths=normalized_paths,
            proposed_paths=proposed_paths,
            ambiguous=False,
            reasons=["legacy Agent_Red path evidence repathed to applications/Agent_Red/"],
        )

    if text_mentions_agent_red and generic_paths:
        return ScopeClassification(
            proposed_scope=None,
            normalized_paths=normalized_paths,
            proposed_paths=proposed_paths,
            ambiguous=True,
            reasons=["Agent Red text with generic top-level path evidence"],
        )

    return ScopeClassification(
        proposed_scope=None,
        normalized_paths=normalized_paths,
        proposed_paths=proposed_paths,
        ambiguous=False,
        reasons=["path evidence is not Agent Red application-specific"],
    )


def scope_path_violations(scope: str | None, paths: list[str]) -> list[str]:
    """Return human-readable violations for an explicit application_scope."""
    normalized_scope = validate_application_scope(scope)
    normalized_paths = [normalize_repo_path(path) for path in paths if path and path.strip()]
    if normalized_scope is None:
        return []
    if normalized_scope == AGENT_RED_APPLICATION_SCOPE:
        if not normalized_paths:
            return ["agent_red_application scope requires path evidence under applications/Agent_Red/"]
        return [
            f"agent_red_application path outside applications/Agent_Red/: {path}"
            for path in normalized_paths
            if not is_agent_red_application_path(path)
        ]
    if normalized_scope == GTKB_PLATFORM_SCOPE:
        return [
            f"gtkb_platform path points at applications/Agent_Red/: {path}"
            for path in normalized_paths
            if is_agent_red_application_path(path)
        ]
    return []
