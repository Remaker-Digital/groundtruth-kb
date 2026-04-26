"""Shared helpers for the Phase 8 isolation rehearsal sub-scripts.

Per ``bridge/gtkb-isolation-016-phase8-rehearsal-implementation-013.md``
(REVISED-6) and ``-014`` (Codex GO). Implements the target-root safety
discipline backed by ``ADR-ISOLATION-APPLICATION-PLACEMENT-001`` (upstream
commit ``affa5a0567a64f79bb4c5aae891889d4af50a72a``).
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any


LEGACY_ROOT: Path = Path(__file__).resolve().parents[2]
"""The current project root, equal to the legacy mixed root for Agent Red."""

APPLICATIONS_NAMESPACE: Path = LEGACY_ROOT / "applications"
"""ADR-ISOLATION-APPLICATION-PLACEMENT-001 namespace under <gt-kb-root>/."""

TARGET_ROOT_DEFAULT: Path = APPLICATIONS_NAMESPACE / "Agent_Red"
"""Default target root for Agent Red rehearsal per ADR + S310 owner directive."""


# Per `-013` §2: explicit blocklist enumeration. Each entry is a top-level
# directory at <gt-kb-root>/<name>/ that contains Agent Red content mixed
# with or alongside GT-KB infrastructure. Adding new entries requires
# deliberate review.
LEGACY_CONFLATED_SURFACES: frozenset[str] = frozenset(
    {
        "src",
        "admin",
        "bridge",
        "tests",
        "docs",
        "infrastructure",
        "extensions",
        "tools",
        "evaluation",
        "assets",
        "branding",
        "legal",
        "prototype",
        "pacts",
        "output",
        "test_host",
        "test-results",
        "node_modules",
        "tmp",
        "archive",
        "independent-progress-assessments",
        "drafts",
        "img",
        "logs",
        "agent-red.wiki",
        "docs-site",
        "config",
        "memory",
        # Added per Codex `-012` non-blocking note (verified via
        # `git ls-tree --name-only -d HEAD`):
        "scripts",
        "website",
        "widget",
    }
)

VALID_NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
"""Per ADR §Decision: <name> must match this identifier shape."""


class TargetRootError(ValueError):
    """Raised when ``--target-root`` violates the placement-rule contract."""


class ManifestError(ValueError):
    """Raised when the rehearsal manifest is malformed or self-inconsistent."""


def is_within(child: Path, ancestor: Path) -> bool:
    """Return True iff ``child`` is the same as or a descendant of ``ancestor``."""
    try:
        child.resolve().relative_to(ancestor.resolve())
        return True
    except ValueError:
        return False


def validate_target_root(path: Path) -> None:
    """Enforce the ADR-backed placement rule via positive allow.

    Per Codex `-014` GO condition: this MUST be a positive allow rule, not a
    blocklist-only check. Target roots under ``<gt-kb-root>/`` are valid only
    when they resolve under ``<gt-kb-root>/applications/<name>/`` with a valid
    ``<name>``. The blocklist (``LEGACY_CONFLATED_SURFACES``) is useful
    evidence but not the only protection — future top-level directories not
    yet in the blocklist will still be refused.

    Raises ``TargetRootError`` on violation.
    """
    resolved = path.resolve()
    legacy = LEGACY_ROOT.resolve()

    # Outside <gt-kb-root>/ entirely is allowed (e.g., a scratch sandbox).
    # The ADR's placement rule binds adopters under GT-KB but does not
    # forbid rehearsals from running against an unrelated tree (e.g., for
    # tests). This rehearsal is for Agent Red, so the canonical target IS
    # under <gt-kb-root>/applications/Agent_Red/.
    if not is_within(resolved, legacy):
        return

    # Inside <gt-kb-root>/: enforce the ADR rule.
    if resolved == legacy:
        raise TargetRootError(
            f"target-root cannot be the legacy mixed root itself ({legacy}). "
            f"Per ADR-ISOLATION-APPLICATION-PLACEMENT-001, adopter applications "
            f"live at <gt-kb-root>/applications/<name>/."
        )

    namespace = APPLICATIONS_NAMESPACE.resolve()
    if resolved == namespace:
        raise TargetRootError(
            f"target-root cannot be the applications/ parent itself ({namespace}). "
            f"Specify a named child: <gt-kb-root>/applications/<name>/."
        )

    if not is_within(resolved, namespace):
        # Inside <gt-kb-root>/ but not under applications/. Definitely a
        # conflated surface (or a new top-level directory). Refuse.
        try:
            relative = resolved.relative_to(legacy)
            top = relative.parts[0] if relative.parts else "(root)"
        except ValueError:
            top = "(unknown)"
        if top in LEGACY_CONFLATED_SURFACES:
            raise TargetRootError(
                f"target-root resolves inside conflated legacy surface "
                f"{top!r} ({resolved}). Per ADR-ISOLATION-APPLICATION-PLACEMENT-001, "
                f"adopter applications live only at "
                f"<gt-kb-root>/applications/<name>/."
            )
        raise TargetRootError(
            f"target-root {resolved} resolves inside <gt-kb-root>/ but outside "
            f"the applications/ namespace. Per ADR-ISOLATION-APPLICATION-PLACEMENT-001, "
            f"the only allowed location is <gt-kb-root>/applications/<name>/."
        )

    # Inside applications/: must have a named child matching the ADR pattern.
    relative = resolved.relative_to(namespace)
    if not relative.parts:
        raise TargetRootError(
            f"target-root cannot be the applications/ parent ({namespace}). "
            f"Specify a named child."
        )
    name = relative.parts[0]
    if not VALID_NAME_PATTERN.match(name):
        raise TargetRootError(
            f"adopter <name> {name!r} does not match the ADR identifier "
            f"pattern ^[A-Za-z][A-Za-z0-9_-]*$ "
            f"(per ADR-ISOLATION-APPLICATION-PLACEMENT-001 §Decision)."
        )


def hash_set_walk(root: Path, ignored_top_level: frozenset[str] | None = None) -> dict[str, str]:
    """Walk ``root`` and return ``{relative_path: sha256(file_bytes)}``.

    Used pre/post rehearsal to detect drift on the legacy mixed root. Symlinks
    not followed; binary content hashed normally.
    """
    if ignored_top_level is None:
        ignored_top_level = frozenset({".git", "__pycache__", "node_modules", ".groundtruth-chroma", ".tmp.driveupload"})
    result: dict[str, str] = {}
    if not root.exists() or not root.is_dir():
        return result
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        try:
            rel = path.relative_to(root)
        except ValueError:
            continue
        if rel.parts and rel.parts[0] in ignored_top_level:
            continue
        try:
            data = path.read_bytes()
        except OSError:
            continue
        result[str(rel).replace("\\", "/")] = hashlib.sha256(data).hexdigest()
    return result


def load_manifest(path: Path) -> dict[str, Any]:
    """Load the rehearsal TOML manifest. Validates ADR-required fields."""
    if not path.exists():
        raise ManifestError(f"manifest not found at {path}")
    try:
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib  # type: ignore[no-redef,import-not-found]
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ManifestError(f"manifest at {path} could not be parsed: {exc}") from exc

    target_root_str = data.get("target_root")
    legacy_root_str = data.get("legacy_root")
    applications_namespace_str = data.get("applications_namespace")

    if not isinstance(target_root_str, str):
        raise ManifestError("manifest.target_root must be a string")
    if not isinstance(legacy_root_str, str):
        raise ManifestError("manifest.legacy_root must be a string")
    if not isinstance(applications_namespace_str, str):
        raise ManifestError("manifest.applications_namespace must be a string")

    legacy = Path(legacy_root_str).resolve()
    namespace = Path(applications_namespace_str).resolve()
    expected_namespace = (legacy / "applications").resolve()
    if namespace != expected_namespace:
        raise ManifestError(
            f"manifest.applications_namespace ({namespace}) must equal "
            f"<legacy_root>/applications ({expected_namespace})"
        )

    target = Path(target_root_str).resolve()
    if not is_within(target, namespace):
        raise ManifestError(
            f"manifest.target_root ({target}) must be a descendant of "
            f"applications_namespace ({namespace})"
        )

    return data
