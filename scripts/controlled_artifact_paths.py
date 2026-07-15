"""Shared controlled-artifact path classification for GT-KB mutation gates."""

from __future__ import annotations

import re
from dataclasses import dataclass

PROTECTED_EXACT = frozenset(
    {
        ".claude/settings.json",
        ".codex/hooks.json",
        ".env",
        "env.local",
        "env.staging",
        "pyproject.toml",
        "groundtruth.toml",
        "Dockerfile",
        "Dockerfile.test",
        "Dockerfile.ui",
        ".dockerignore",
        "docker-compose.yml",
        "shopify.app.toml",
    }
)
PROTECTED_PREFIXES = (
    "scripts/",
    "groundtruth-kb/src/",
    "groundtruth-kb/tests/",
    "platform_tests/",
    "tests/",
    ".claude/hooks/",
    ".claude/rules/",
    ".codex/gtkb-hooks/",
    "config/",
    ".github/",
)
ALLOWED_WRITE_PREFIXES = (
    "bridge/",
    "independent-progress-assessments/",
)
DIAGNOSTIC_WRITE_PREFIXES = (
    ".groundtruth/session/snapshots/",
    ".gtkb-state/",
)
DISPATCHER_CONFIG_PATH = "config/dispatcher/rules.toml"

VERSIONED_BRIDGE_FILE_RE = re.compile(r"^bridge/[A-Za-z0-9][A-Za-z0-9_.-]*-\d{3}\.md$")
BRIDGE_STATUS_ARTIFACT_COMMAND_PATTERN = (
    r"(?:[A-Za-z]:)?(?:[\\/]|[\w .-]+[\\/])*bridge[\\/]"
    r"(?:[A-Za-z0-9][A-Za-z0-9_.-]*-\d{3}\.md|INDEX\.md)"
)

ROOT_MEMBASE_EXACT = frozenset({"groundtruth.db"})
RUNTIME_AUTHORITY_PREFIXES = (
    "harness-state/",
    ".gtkb-state/implementation-authorizations/",
    ".gtkb-state/work-intent/",
    ".gtkb-state/bridge-poller/",
    ".gtkb-state/dispatcher-daemon/",
    ".gtkb-state/dispatch/",
    ".gtkb-state/git-lifecycle/",
    ".gtkb-state/modernization-release-candidate/",
)


@dataclass(frozen=True)
class ControlledArtifactClassification:
    """Result of classifying one workspace-relative path."""

    normalized_path: str
    is_controlled: bool
    direct_write_blocked: bool
    reason_code: str
    classification: str


def normalize_relative_path_text(relative_path: str) -> str:
    """Normalize a workspace-relative path without dropping leading dot paths."""
    rel = str(relative_path).strip().strip("'\"`").replace("\\", "/")
    while rel.startswith("./"):
        rel = rel[2:]
    return rel


def is_versioned_bridge_status_file(relative_path: str) -> bool:
    return VERSIONED_BRIDGE_FILE_RE.fullmatch(normalize_relative_path_text(relative_path)) is not None


def is_bridge_status_artifact_path(relative_path: str) -> bool:
    rel = normalize_relative_path_text(relative_path)
    return rel == "bridge/INDEX.md" or is_versioned_bridge_status_file(rel)


def is_runtime_authority_state_path(relative_path: str) -> bool:
    rel = normalize_relative_path_text(relative_path)
    return rel in ROOT_MEMBASE_EXACT or any(rel.startswith(prefix) for prefix in RUNTIME_AUTHORITY_PREFIXES)


def classify_controlled_artifact(relative_path: str) -> ControlledArtifactClassification:
    rel = normalize_relative_path_text(relative_path)
    if rel == "<unknown-mutating-target>":
        return ControlledArtifactClassification(rel, True, False, "unknown_mutating_target", rel)
    if rel == "bridge/INDEX.md":
        return ControlledArtifactClassification(
            rel,
            True,
            True,
            "bridge_index_direct_mutation",
            "bridge/INDEX.md",
        )
    if is_versioned_bridge_status_file(rel):
        return ControlledArtifactClassification(
            rel,
            True,
            True,
            "bridge_status_file_direct_mutation",
            "bridge/<slug>-NNN.md",
        )
    if rel == "groundtruth.db":
        return ControlledArtifactClassification(
            rel,
            True,
            True,
            "membase_direct_mutation",
            "groundtruth.db",
        )
    for prefix in RUNTIME_AUTHORITY_PREFIXES:
        if rel.startswith(prefix):
            return ControlledArtifactClassification(
                rel,
                True,
                True,
                "runtime_authority_state_direct_mutation",
                prefix,
            )
    if rel in PROTECTED_EXACT:
        return ControlledArtifactClassification(rel, True, False, "protected_path", rel)
    if rel.startswith(".env."):
        return ControlledArtifactClassification(rel, True, False, "protected_path", ".env.*")
    if rel.startswith(ALLOWED_WRITE_PREFIXES):
        return ControlledArtifactClassification(rel, False, False, "not_protected", rel)
    if rel.startswith(DIAGNOSTIC_WRITE_PREFIXES):
        return ControlledArtifactClassification(rel, False, False, "not_protected", rel)
    for prefix in PROTECTED_PREFIXES:
        if rel.startswith(prefix):
            return ControlledArtifactClassification(rel, True, False, "protected_path", prefix)
    return ControlledArtifactClassification(rel, False, False, "not_protected", rel)


def is_protected_path(relative_path: str) -> bool:
    return classify_controlled_artifact(relative_path).is_controlled


def direct_write_block_reason_code(paths: list[str]) -> str | None:
    reason_codes = {
        classification.reason_code
        for path in paths
        if (classification := classify_controlled_artifact(path)).direct_write_blocked
    }
    if not reason_codes:
        return None
    if len(reason_codes) == 1:
        return next(iter(reason_codes))
    return "controlled_artifact_direct_mutation"


def protected_path_classification(relative_path: str) -> str:
    return classify_controlled_artifact(relative_path).classification


__all__ = [
    "ALLOWED_WRITE_PREFIXES",
    "BRIDGE_STATUS_ARTIFACT_COMMAND_PATTERN",
    "ControlledArtifactClassification",
    "DIAGNOSTIC_WRITE_PREFIXES",
    "DISPATCHER_CONFIG_PATH",
    "PROTECTED_EXACT",
    "PROTECTED_PREFIXES",
    "RUNTIME_AUTHORITY_PREFIXES",
    "classify_controlled_artifact",
    "direct_write_block_reason_code",
    "is_bridge_status_artifact_path",
    "is_protected_path",
    "is_runtime_authority_state_path",
    "is_versioned_bridge_status_file",
    "normalize_relative_path_text",
    "protected_path_classification",
]
