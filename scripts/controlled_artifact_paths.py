"""Shared controlled-artifact path classification for GT-KB mutation gates."""

from __future__ import annotations

import re
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from groundtruth_kb.project.registry_control_plane import (
    RegistryControlPlaneError,
    load_registry_snapshot,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# WI-5742 Layer B1: invocation-scoped registry snapshot cache.
#
# ``load_registry_snapshot`` acquires the *exclusive* control-plane file lock
# even though classification is a pure read. Classifying an N-path staged set
# therefore performed N (plus one for the registry commit assessment) exclusive
# lock acquisitions and N full snapshot parses of a 1.55 MB registry TOML over
# an 844 MB store. That is both a CPU cost and the contention amplifier behind
# the observed ``timed out acquiring registry lock ... control-plane.lock``
# failures.
#
# The cache is DISABLED by default (``None``) so no existing caller changes
# behavior. A caller that is performing one bounded, read-only evaluation opens
# :func:`registry_snapshot_cache_scope` for the duration of that single
# invocation, collapsing N+1 loads to 1. The cache never outlives the scope and
# is never process-global: a global cache would open a stale-authority window
# for mutating callers, which was rejected in the WI-5742 proposal.
_REGISTRY_SNAPSHOT_CACHE: dict[str, Any] | None = None


@contextmanager
def registry_snapshot_cache_scope() -> Iterator[None]:
    """Memoize registry snapshot loads for the duration of one read-only invocation.

    Re-entrant by save/restore, so a nested scope cannot leak a cache into an
    enclosing caller that did not ask for one.
    """
    global _REGISTRY_SNAPSHOT_CACHE
    previous = _REGISTRY_SNAPSHOT_CACHE
    _REGISTRY_SNAPSHOT_CACHE = {}
    try:
        yield
    finally:
        _REGISTRY_SNAPSHOT_CACHE = previous


def load_registry_snapshot_cached(*, project_root: Path) -> Any:
    """Load a registry snapshot, reusing one already loaded in the active cache scope.

    Outside a :func:`registry_snapshot_cache_scope` this is exactly
    ``load_registry_snapshot`` -- same lock, same freshness, no caching.
    """
    if _REGISTRY_SNAPSHOT_CACHE is None:
        return load_registry_snapshot(project_root=project_root)
    key = str(Path(project_root).resolve())
    if key not in _REGISTRY_SNAPSHOT_CACHE:
        _REGISTRY_SNAPSHOT_CACHE[key] = load_registry_snapshot(project_root=project_root)
    return _REGISTRY_SNAPSHOT_CACHE[key]


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
    ".harness-baseline-configuration/hooks/",
    ".harness-baseline-configuration/rules/",
    ".agents/skills/",
    "config/",
    ".github/",
)
ALLOWED_WRITE_PREFIXES = (
    "bridge/",
    "independent-progress-assessments/",
)
DIAGNOSTIC_WRITE_PREFIXES = (".groundtruth/session/snapshots/",)

VERSIONED_BRIDGE_FILE_RE = re.compile(r"^bridge/[A-Za-z0-9][A-Za-z0-9_.-]*-\d{3}\.md$")
BRIDGE_STATUS_ARTIFACT_COMMAND_PATTERN = (
    r"(?:[A-Za-z]:)?(?:[\\/]|[\w .-]+[\\/])*bridge[\\/]"
    r"(?:[A-Za-z0-9][A-Za-z0-9_.-]*-\d{3}\.md|INDEX\.md)"
)

ROOT_MEMBASE_EXACT = frozenset({"groundtruth.db"})
# Neither retired local-state tree is a permissible direct-write target.
RUNTIME_AUTHORITY_PREFIXES = (
    "harness-state/",
    ".gtkb-state/",
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


def _registry_classification(rel: str, project_root: Path) -> ControlledArtifactClassification | None:
    registry_path = project_root / "config" / "registry" / "sot-artifacts.toml"
    if not registry_path.exists():
        return None
    try:
        record = load_registry_snapshot_cached(project_root=project_root).resolver.resolve(rel)
    except RegistryControlPlaneError:
        return ControlledArtifactClassification(rel, True, True, "registry_authority_unavailable", "registry/error")
    if record is None:
        return None
    return ControlledArtifactClassification(rel, True, False, "registered_artifact", f"registry:{record.id}")


def classify_controlled_artifact(
    relative_path: str, *, project_root: Path | None = None
) -> ControlledArtifactClassification:
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
        if rel == prefix.rstrip("/") or rel.startswith(prefix):
            return ControlledArtifactClassification(
                rel,
                True,
                True,
                "runtime_authority_state_direct_mutation",
                prefix,
            )
    registered = _registry_classification(rel, (project_root or PROJECT_ROOT).resolve())
    if registered is not None:
        return registered
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


def is_protected_path(relative_path: str, *, project_root: Path | None = None) -> bool:
    return classify_controlled_artifact(relative_path, project_root=project_root).is_controlled


def direct_write_block_reason_code(paths: list[str], *, project_root: Path | None = None) -> str | None:
    reason_codes = {
        classification.reason_code
        for path in paths
        if (classification := classify_controlled_artifact(path, project_root=project_root)).direct_write_blocked
    }
    if not reason_codes:
        return None
    if len(reason_codes) == 1:
        return next(iter(reason_codes))
    return "controlled_artifact_direct_mutation"


def protected_path_classification(relative_path: str, *, project_root: Path | None = None) -> str:
    return classify_controlled_artifact(relative_path, project_root=project_root).classification


__all__ = [
    "ALLOWED_WRITE_PREFIXES",
    "BRIDGE_STATUS_ARTIFACT_COMMAND_PATTERN",
    "ControlledArtifactClassification",
    "DIAGNOSTIC_WRITE_PREFIXES",
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
