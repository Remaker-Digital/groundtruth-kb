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


# Wave 2 Slice 1 validation constants (per
# bridge/gtkb-isolation-016-phase8-wave2-slice1-002.md GO).

_OUTPUT_DIR_ALLOWLIST_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^[A-Z]:[/\\]temp[/\\]agent-red-rehearsal", re.IGNORECASE),
    re.compile(r"^/tmp/agent-red-rehearsal"),
)

_OUTPUT_DIR_ALLOWLIST_DESC: str = (
    "C:/temp/agent-red-rehearsal* or /tmp/agent-red-rehearsal* "
    "(extend _OUTPUT_DIR_ALLOWLIST_PATTERNS for additional sandbox paths)"
)

_VALID_GIT_STRATEGIES: frozenset[str] = frozenset({"fresh_repo", "clone_with_history_filter", "clean_worktree"})

# Wave 3 validation constants per
# bridge/gtkb-isolation-016-phase8-wave3-execution-007.md (REVISED-3, GO -008).
# Encodes DELIB-S325-DB-RECONCILIATION-STRATEGY-CHOICE and
# DELIB-S325-UNCLASSIFIED-DISPOSITION-CHOICE.
_VALID_DB_RECONCILIATION_STRATEGIES: frozenset[str] = frozenset(
    {
        "manifest_driven_filter",
    }
)
_VALID_UNCLASSIFIED_DISPOSITIONS: frozenset[str] = frozenset(
    {
        "leave_behind_with_warning",
        "carry_forward_to_adopter",
        "manual_review_gate",
    }
)

_CLONE_FILTER_REQUIRED_PLACEHOLDERS: tuple[str, ...] = (
    "<agent-red-paths-from-_path_rewrite>",
    "<each-source>",
    "<each-target>",
    "git filter-repo --path",
)


def _is_allowed_output_dir(path: Path) -> bool:
    """Return True iff ``path`` matches one of the sandbox allowlist patterns."""
    s = str(path)
    return any(p.match(s) for p in _OUTPUT_DIR_ALLOWLIST_PATTERNS)


def validate_sandbox_output_dir(output_dir: Path) -> None:
    """Apply M2 sandbox-safety rules to an output_dir path.

    Raises ``ManifestValidationError`` on violation. Used from both
    :func:`load_manifest` (for ``manifest.output_dir``) and from the
    rehearsal driver (for ``--output-dir`` CLI override). Same rules;
    same enforcement.

    Per ``bridge/gtkb-isolation-016-phase8-wave2-slice3-003.md`` F2 fix:
    extracting this helper lets the driver enforce M2 safety on operator-
    provided override paths before any file writes.
    """
    if is_within(output_dir, TARGET_ROOT_DEFAULT):
        raise ManifestValidationError(
            f"M2: output_dir ({output_dir}) cannot be under "
            f"TARGET_ROOT_DEFAULT ({TARGET_ROOT_DEFAULT}); must be a "
            f"sandbox path."
        )
    if is_within(output_dir, LEGACY_ROOT):
        raise ManifestValidationError(
            f"M2: output_dir ({output_dir}) cannot be under LEGACY_ROOT ({LEGACY_ROOT}); must be a sandbox path."
        )
    if not _is_allowed_output_dir(output_dir):
        raise ManifestValidationError(
            f"M2: output_dir ({output_dir}) does not match the sandbox "
            f"allowlist; permitted patterns: {_OUTPUT_DIR_ALLOWLIST_DESC}."
        )


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


class ManifestValidationError(ManifestError):
    """Raised when a loaded manifest violates a Wave 2 validation rule (M1-M5).

    Subclasses ``ManifestError`` so callers that catch ``ManifestError`` continue
    to work without modification (no breaking change for Wave 1 call sites).
    """


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
        raise TargetRootError(f"target-root cannot be the applications/ parent ({namespace}). Specify a named child.")
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
        ignored_top_level = frozenset(
            {".git", "__pycache__", "node_modules", ".groundtruth-chroma", ".tmp.driveupload"}
        )
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


def load_manifest(
    path: Path,
    *,
    wave: int = 1,
    is_runtime_manifest: bool = False,
) -> dict[str, Any]:
    """Load the rehearsal TOML manifest. Validates ADR-required fields.

    The ``wave`` keyword (default 1) preserves Wave 1 driver behavior. Pass
    ``wave=2`` to enforce the Slice 1 validation rules M1-M5; pass ``wave=3``
    to additionally reject the unresolved ``db_reconciliation_strategy``
    placeholder.

    The ``is_runtime_manifest`` keyword (default False) extends M5 at
    ``wave>=2`` to require non-empty ``surface_treatments``. Per Slice 2
    contract, ``_inventory.py`` is the only call site that should pass
    ``is_runtime_manifest=True`` — it does so to revalidate its own runtime
    manifest after populating ``surface_treatments`` from the authority
    matrix.

    Per ``bridge/gtkb-isolation-016-phase8-wave2-slice1-002.md`` GO:
    Wave 2 guarantees apply only to call sites that explicitly pass
    ``wave=2`` or later. The mere existence of this helper does not mean
    every consumer has been validated.
    """
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
            f"manifest.target_root ({target}) must be a descendant of applications_namespace ({namespace})"
        )

    # Wave 2 validation rules M1-M5 per Slice 1 GO -002.
    # Gated by the ``wave`` parameter so Wave 1 callers retain existing behavior.
    if wave >= 2:
        # Rule M1 — No OWNER_DECISION_REQUIRED placeholders in fields blocking
        # the requested wave. db_reconciliation_strategy surfaces at wave>=3
        # (Wave 3 verification matrix boundary), not Wave 2.
        for blocking_field in ("output_dir", "git_strategy"):
            value = data.get(blocking_field)
            if value == "OWNER_DECISION_REQUIRED":
                raise ManifestValidationError(
                    f"M1: manifest.{blocking_field} = 'OWNER_DECISION_REQUIRED' "
                    f"blocks Wave {wave}; resolve owner decision before re-running."
                )
        if wave >= 3:
            if data.get("db_reconciliation_strategy") == "OWNER_DECISION_REQUIRED":
                raise ManifestValidationError(
                    "M1: manifest.db_reconciliation_strategy = "
                    "'OWNER_DECISION_REQUIRED' blocks Wave 3; resolve §3.6 "
                    "owner decision before re-running."
                )

            # Rule M6 — db_reconciliation_strategy and unclassified_disposition
            # positive validation. Rejects any value not in the known set, not
            # just the OWNER_DECISION_REQUIRED placeholder. Per
            # bridge/gtkb-isolation-016-phase8-wave3-execution-007.md.
            strategy = data.get("db_reconciliation_strategy")
            if strategy not in _VALID_DB_RECONCILIATION_STRATEGIES:
                raise ManifestValidationError(
                    f"M6: manifest.db_reconciliation_strategy = {strategy!r} "
                    f"not in {sorted(_VALID_DB_RECONCILIATION_STRATEGIES)}."
                )
            disposition = data.get("unclassified_disposition")
            if disposition not in _VALID_UNCLASSIFIED_DISPOSITIONS:
                raise ManifestValidationError(
                    f"M6: manifest.unclassified_disposition = {disposition!r} "
                    f"not in {sorted(_VALID_UNCLASSIFIED_DISPOSITIONS)}."
                )

        # Rule M2 — output_dir safety: must not be under LEGACY_ROOT or
        # TARGET_ROOT_DEFAULT; must match the sandbox allowlist.
        output_dir_str = data.get("output_dir")
        if not isinstance(output_dir_str, str):
            raise ManifestValidationError("M2: manifest.output_dir must be a string")
        output_dir = Path(output_dir_str)
        # Per Slice 3 F2 fix: M2 enforcement extracted into
        # validate_sandbox_output_dir() so the driver can apply the same
        # rules to --output-dir CLI overrides. Functionally identical to
        # the pre-Slice-3 inline checks.
        validate_sandbox_output_dir(output_dir)

        # Rule M3 — git_strategy must be valid; clone_with_history_filter
        # requires git_filter_command_template with required placeholders.
        git_strategy = data.get("git_strategy")
        if git_strategy not in _VALID_GIT_STRATEGIES:
            raise ManifestValidationError(
                f"M3: manifest.git_strategy = {git_strategy!r} not in {sorted(_VALID_GIT_STRATEGIES)}."
            )
        if git_strategy == "clone_with_history_filter":
            template = data.get("git_filter_command_template", "")
            if not isinstance(template, str):
                raise ManifestValidationError(
                    "M3: manifest.git_filter_command_template must be a "
                    "string when git_strategy = 'clone_with_history_filter'."
                )
            for required in _CLONE_FILTER_REQUIRED_PLACEHOLDERS:
                if required not in template:
                    raise ManifestValidationError(
                        f"M3: manifest.git_filter_command_template missing "
                        f"required placeholder {required!r} for "
                        f"clone_with_history_filter."
                    )

        # Rule M4 — phase_1_authority_matrix_path must exist relative to
        # repo root.
        matrix_path_str = data.get("phase_1_authority_matrix_path")
        if not isinstance(matrix_path_str, str):
            raise ManifestValidationError("M4: manifest.phase_1_authority_matrix_path must be a string.")
        matrix_path = LEGACY_ROOT / matrix_path_str
        if not matrix_path.exists():
            raise ManifestValidationError(
                f"M4: manifest.phase_1_authority_matrix_path resolves to {matrix_path} which does not exist on disk."
            )

        # Rule M5 — surface_treatments shape:
        #   - Source manifest (default): empty allowed; non-dict rejected.
        #   - Runtime manifest (is_runtime_manifest=True): non-empty required.
        # The runtime-manifest enforcement was deferred from Slice 1 to Slice 2
        # per Slice 1 GO -002 sequencing condition; Slice 2 GO -004 confirms
        # this extension as the only call site that should pass True.
        surface_treatments = data.get("surface_treatments")
        if surface_treatments is None or (isinstance(surface_treatments, dict) and not surface_treatments):
            if is_runtime_manifest:
                raise ManifestValidationError(
                    "M5: runtime manifest requires non-empty surface_treatments; "
                    "Wave 2 lane 1 (_inventory.py) must populate it from the "
                    "authority matrix before downstream lanes can consume it."
                )
            # Source manifest: empty/missing acceptable — normalize to {}.
            if surface_treatments is None:
                data["surface_treatments"] = {}
        elif not isinstance(surface_treatments, dict):
            raise ManifestValidationError(
                "M5: manifest.surface_treatments must be a TOML table (dict in Python) when present."
            )

    return data
