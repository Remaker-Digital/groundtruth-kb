# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Project upgrade — ``gt project upgrade`` implementation.

All managed artifacts (hooks, rules, skills, settings-hook-registrations,
and gitignore-patterns) are sourced from
:mod:`groundtruth_kb.project.managed_registry`, which parses the declarative
TOML file at ``templates/managed-artifacts.toml``. The registry is the
single source of truth for scaffold / upgrade / doctor lifecycle behavior.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from groundtruth_kb import __version__, get_templates_dir
from groundtruth_kb.project.doctor import ToolCheck
from groundtruth_kb.project.doctor_isolation import run_isolation_checks
from groundtruth_kb.project.managed_registry import (
    FileArtifact,
    GitignorePattern,
    SettingsHookRegistration,
    artifacts_for_upgrade,
)
from groundtruth_kb.project.manifest import read_manifest, write_manifest
from groundtruth_kb.project.profiles import get_profile
from groundtruth_kb.project.rollback import (
    ReceiptJSON,
    resolve_receipt_mode,
    write_receipt,
)

# Upgrade policies that produce no upgrade-time action at all. Rows whose
# ``ownership.upgrade_policy`` is in this set are filtered out of the plan
# before each phase runs. Policy metadata is attached to every parsed
# artifact by the managed-registry loader (GO C2 — no parallel raw-TOML
# parser). All 40 current-HEAD registry rows have ``upgrade_policy`` in
# ``{overwrite, structured-merge}`` and are unaffected by this filter.
_NO_UPGRADE_ACTION_POLICIES: frozenset[str] = frozenset({"preserve", "transient", "adopter-opt-in"})


# ---------------------------------------------------------------------------
# GTKB-ISOLATION-017 Slice 4 — isolation pre-flight + auto-fixer dispatch.
# Authority: bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-008.md (GO).
# Prior decisions: DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE
# (mandatory_at_upgrade / one_shot_migration_at_upgrade / out_of_band_recipe_only)
# + S328 owner AskUserQuestion answer authorizing --accept-migration override of
# upgrade_policy=preserve for the bounded isolation-fix surface.
# ---------------------------------------------------------------------------

# Live-probed partition of the 9 isolation doctor checks per
# ``run_isolation_checks()`` (see bridge -011 §"Live-probed partition + surface").
# Total: 1 + 4 + 4 = 9 = the live check universe (T11 enforces).
# Check #5 (`isolation:hooks-point-to-wrappers`) reclassified from
# auto-fixable to needs-adopter-input in REVISED-4 (`-011`) per Codex
# `-010` NO-GO + S328 owner reclassify decision.
_PARTITION_HARD_REFUSE: frozenset[str] = frozenset(
    {
        "isolation:adopter-root-placement",
    }
)
_PARTITION_AUTO_FIXABLE: frozenset[str] = frozenset(
    {
        "isolation:service-endpoint",
        "isolation:work-subject",
        "isolation:workstream-focus-hook-absent",
        "isolation:release-readiness-app-subject-header",
    }
)
# Per Codex `-010` NO-GO + S328 owner remediation choice (reclassify, not
# aggressive-fixer): isolation:hooks-point-to-wrappers moved here from
# auto-fixable. The `_compute_target_event_list` machinery cannot reliably
# clear all live check-#5 warning modes (specifically adopter-owned
# non-wrapper hooks); rather than deleting adopter customizations
# destructively, the upgrade refuses with adopter-input guidance.
_PARTITION_NEEDS_ADOPTER_INPUT: frozenset[str] = frozenset(
    {
        "isolation:no-writable-product-paths",
        "isolation:hooks-point-to-wrappers",
        "isolation:chroma-regeneratable",
    }
)

# The exact relative paths the 4 isolation auto-fixers may touch. Defense in
# depth against scope creep: each helper asserts its target file is in this
# set before mutating. Owner decision required to extend; see DELIB-S328.
#
# Live-probe correction (post-impl S328): check #3 reads
# .claude/session/work-subject.json (canonical Phase 7 durable state),
# NOT the TOML's [durable_state] block. The fixer therefore writes the
# JSON file and the TOML's `work_subject = "application"` is no longer
# the authority. Same defect class as -006 F1.
_ISOLATION_FIX_SURFACE_FILES: frozenset[str] = frozenset(
    {
        "groundtruth.toml",  # touched by check #2 (service endpoint)
        ".claude/session/work-subject.json",  # touched by check #3 (work subject)
        ".claude/hooks/workstream-focus.py",  # touched by check #6 (DELETED, not modified)
        "memory/release-readiness.md",  # touched by check #8
    }
)
# Note: `.claude/settings.json` previously listed for check #5 was removed in
# REVISED-4 (`-011`) when check #5 reclassified to needs-adopter-input per
# Codex `-010` NO-GO + S328 owner choice.

# Files in the isolation-fix surface whose `upgrade_policy=preserve` is
# overridden ONLY when --accept-migration is set. Recorded in the rollback
# receipt's `prior_policy` field for adopter audit.
_ISOLATION_FIX_PRESERVE_OVERRIDE_FILES: frozenset[str] = frozenset(
    {
        "groundtruth.toml",
        "memory/release-readiness.md",
    }
)


@dataclass
class IsolationPreflightResult:
    """Output of :func:`_run_isolation_preflight` — partitioned failing checks.

    Only checks with ``status in {"fail", "warning"}`` are included; ``pass``
    and ``info`` are dropped (no work to do). The partition is exhaustive over
    the live check universe per the partition-contract test (T11).
    """

    hard_refuse: list[ToolCheck] = field(default_factory=list)
    auto_fixable: list[ToolCheck] = field(default_factory=list)
    needs_adopter_input: list[ToolCheck] = field(default_factory=list)


@dataclass
class IsolationFixerResult:
    """One auto-fixer's outcome — passed back from the typed dispatcher.

    Recorded in the rollback receipt's ``isolation_migration.auto_fixed``
    list per the F2 audit-trail contract.
    """

    check_name: str
    file: str
    outcome: Literal["fixed", "skipped", "no-op"]
    reason: str
    prior_policy: str  # e.g., "preserve" / "unregistered" / "settings-hook-registration"


class IsolationLocationFailureError(RuntimeError):
    """Raised when the adopter root is under the product root (check #1).

    Cannot be fixed by ``gt project upgrade``. The adopter must relocate the
    application directory to comply with ADR-ISOLATION-APPLICATION-PLACEMENT-001
    (``<gt-kb-root>/applications/<name>/``). Refused regardless of
    ``--accept-migration``.
    """

    def __init__(self, target: Path, hard_refuse_checks: list[ToolCheck]) -> None:
        names = ", ".join(c.name for c in hard_refuse_checks)
        super().__init__(
            f"Cannot upgrade: adopter at {target} fails isolation-location check(s): "
            f"{names}. Per ADR-ISOLATION-APPLICATION-PLACEMENT-001 adopters must "
            f"live at <gt-kb-root>/applications/<name>/. Relocate the adopter "
            f"directory and re-run."
        )
        self.target = target
        self.hard_refuse_checks = hard_refuse_checks


class IsolationMigrationRequiredError(RuntimeError):
    """Raised when isolation checks fail AND ``--accept-migration`` is not set.

    The adopter must opt in to one-shot migration via ``--accept-migration``
    after running the rehearsal recipe out-of-band.
    """

    def __init__(self, target: Path, failing_checks: list[ToolCheck]) -> None:
        names = ", ".join(c.name for c in failing_checks)
        super().__init__(
            f"Isolation migration required at {target}: failing check(s) {names}. "
            f"Run the rehearsal recipe (see CLI output) then re-run with "
            f"--accept-migration to opt in to one-shot migration."
        )
        self.target = target
        self.failing_checks = failing_checks


class IsolationNonAutoFixableError(RuntimeError):
    """Raised when needs-adopter-input checks fail AND ``--accept-migration`` IS set.

    These checks (``isolation:no-writable-product-paths``,
    ``isolation:chroma-regeneratable``) require adopter judgment on
    disposition; the upgrade refuses with per-check guidance.
    """

    def __init__(self, target: Path, needs_adopter_input_checks: list[ToolCheck]) -> None:
        names = ", ".join(c.name for c in needs_adopter_input_checks)
        super().__init__(
            f"Isolation migration cannot complete at {target}: check(s) {names} "
            f"require adopter input. Inspect each check's reported file and "
            f"resolve manually, then re-run."
        )
        self.target = target
        self.needs_adopter_input_checks = needs_adopter_input_checks


class IsolationPolicyOverrideViolation(RuntimeError):
    """Raised if a fixer attempts to mutate a path outside ``_ISOLATION_FIX_SURFACE_FILES``.

    Defense in depth: each fixer asserts its target file is in the surface
    set before mutating. This exception fires only on a bug in the fixer
    helper itself, not on adopter state.
    """

    def __init__(self, attempted_path: str) -> None:
        super().__init__(
            f"IsolationPolicyOverrideViolation: fixer attempted to mutate "
            f"{attempted_path!r}, which is not in _ISOLATION_FIX_SURFACE_FILES. "
            f"Extending the surface requires an owner decision; see DELIB-S328."
        )
        self.attempted_path = attempted_path


def _run_isolation_preflight(
    target: Path,
    profile: str,
    product_root: Path,
) -> IsolationPreflightResult:
    """Partition the 9 live isolation doctor checks into hard-refuse / auto-fixable / needs-adopter-input.

    Only checks with ``status in {"fail", "warning"}`` are included in the
    returned partition. Pass + info checks are dropped (no work to do).

    Per bridge ``-007`` §"Live-Probed Partition", the three partition
    constants together cover every live check name; ``T11`` enforces this
    invariant against ``run_isolation_checks()``'s actual return.
    """
    result = IsolationPreflightResult()
    checks = run_isolation_checks(target, profile, product_root=product_root)
    for check in checks:
        if check.status not in ("fail", "warning"):
            continue
        if check.name in _PARTITION_HARD_REFUSE:
            result.hard_refuse.append(check)
        elif check.name in _PARTITION_AUTO_FIXABLE:
            result.auto_fixable.append(check)
        elif check.name in _PARTITION_NEEDS_ADOPTER_INPUT:
            result.needs_adopter_input.append(check)
        # Unknown check names: silently dropped here. T11 catches at test time
        # by failing if the live check universe contains a name not in any
        # partition constant.
    return result


def _assert_in_isolation_surface(file_path: str) -> None:
    """Defense-in-depth assertion for isolation fixers.

    Each fixer calls this before mutating. Raises
    :class:`IsolationPolicyOverrideViolation` if the path is outside the
    bounded surface. This catches helper bugs at runtime.
    """
    if file_path not in _ISOLATION_FIX_SURFACE_FILES:
        raise IsolationPolicyOverrideViolation(file_path)


def _prior_policy_for(file_path: str) -> str:
    """Return the prior_policy label for receipt audit recording.

    Used by every isolation fixer to populate
    ``IsolationFixerResult.prior_policy``. The value goes into the rollback
    receipt's ``isolation_migration.auto_fixed`` entries so adopters can audit
    what was changed under the ``--accept-migration`` governed override.
    """
    if file_path in (".claude/hooks/workstream-focus.py", ".claude/session/work-subject.json"):
        return "unregistered"
    if file_path in _ISOLATION_FIX_PRESERVE_OVERRIDE_FILES:
        return "preserve"
    return "unknown"


def _fix_isolation_service_endpoint(target: Path) -> IsolationFixerResult:
    """Rewrite the [service] endpoint in groundtruth.toml to a scoped URL form.

    Per check #2 (``isolation:service-endpoint``). The check fails when the
    endpoint matches the raw-DB-path pattern; this fixer replaces it with the
    scoped-service-URL placeholder Slice 3 scaffolds.
    """
    rel = "groundtruth.toml"
    _assert_in_isolation_surface(rel)
    toml_path = target / rel
    if not toml_path.exists():
        return IsolationFixerResult(
            check_name="isolation:service-endpoint",
            file=rel,
            outcome="no-op",
            reason="groundtruth.toml absent; nothing to rewrite",
            prior_policy=_prior_policy_for(rel),
        )
    text = toml_path.read_text(encoding="utf-8")
    placeholder = 'endpoint = "configure-me://placeholder/v1"'
    if placeholder in text:
        return IsolationFixerResult(
            check_name="isolation:service-endpoint",
            file=rel,
            outcome="no-op",
            reason="endpoint already at scoped placeholder",
            prior_policy=_prior_policy_for(rel),
        )
    # Naive replacement: locate any line beginning with "endpoint =" within
    # a [service] section, or append a new [service] block. Adopter-side
    # raw-DB endpoints take many shapes; the scaffold's bracketed-section
    # rewrite gives a deterministic post-state.
    lines = text.splitlines(keepends=False)
    out: list[str] = []
    in_service_section = False
    endpoint_replaced = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            in_service_section = stripped == "[service]"
            out.append(line)
            continue
        if in_service_section and stripped.startswith("endpoint"):
            out.append(placeholder)
            endpoint_replaced = True
            continue
        out.append(line)
    if not endpoint_replaced:
        # No [service] block at all — append one.
        out.extend(["", "[service]", placeholder])
    toml_path.write_text("\n".join(out) + "\n", encoding="utf-8")
    return IsolationFixerResult(
        check_name="isolation:service-endpoint",
        file=rel,
        outcome="fixed",
        reason="endpoint rewritten to scoped placeholder; preserve policy overridden under --accept-migration",
        prior_policy=_prior_policy_for(rel),
    )


def _fix_isolation_work_subject(target: Path) -> IsolationFixerResult:
    """Write canonical Phase 7 durable state at .claude/session/work-subject.json.

    Per check #3 (``isolation:work-subject``). The doctor check reads
    ``<target>/.claude/session/work-subject.json`` (canonical) or
    ``<target>/.claude/hooks/.workstream-focus-state.json`` (legacy
    fallback) per Phase 7 §"Durable State Contract" lines 120-164. The
    check passes when ``current_subject == "application"``.

    This fixer writes the canonical JSON file. The legacy fallback is
    NOT touched; if it exists it remains as adopter-owned migration
    history (check passes via the canonical file taking precedence).
    """
    rel = ".claude/session/work-subject.json"
    _assert_in_isolation_surface(rel)
    state_path = target / rel
    payload = {
        "current_subject": "application",
        "application_root": str(target.resolve()).replace("\\", "/"),
        "set_by": "gt project upgrade --accept-migration",
        "set_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }
    # Idempotent: if the file already says current_subject="application" and
    # the application_root resolves to target, no-op.
    if state_path.exists():
        try:
            existing = json.loads(state_path.read_text(encoding="utf-8"))
            if (
                existing.get("current_subject") == "application"
                and existing.get("application_root")
                and Path(existing["application_root"]).resolve() == target.resolve()
            ):
                return IsolationFixerResult(
                    check_name="isolation:work-subject",
                    file=rel,
                    outcome="no-op",
                    reason="work-subject.json already at canonical state",
                    prior_policy=_prior_policy_for(rel),
                )
        except (OSError, json.JSONDecodeError):
            pass  # Fall through to overwrite.
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return IsolationFixerResult(
        check_name="isolation:work-subject",
        file=rel,
        outcome="fixed",
        reason="wrote canonical Phase 7 work-subject.json with current_subject='application'",
        prior_policy=_prior_policy_for(rel),
    )


# Note: `_fix_isolation_hook_paths` (formerly check #5 fixer) was removed in
# REVISED-4 (`-011`) when `isolation:hooks-point-to-wrappers` was reclassified
# to needs-adopter-input per Codex `-010` NO-GO + S328 owner choice. The
# existing `_compute_target_event_list` machinery in `_execute_merge_event_hooks`
# (used by routine upgrade actions) continues to refresh registry-managed hook
# entries; the isolation-specific dispatcher no longer mutates settings.json.


def _fix_isolation_remove_workstream_focus_hook(target: Path) -> IsolationFixerResult:
    """Delete the deprecated .claude/hooks/workstream-focus.py hook file if present.

    Per check #6 (``isolation:workstream-focus-hook-absent``). Per Phase 9 §4
    line 410 + ADR-ISOLATION-APPLICATION-PLACEMENT-001, the legacy hook is
    deprecated; the doctor warns if it reappears. The file is unregistered
    (out-of-matrix) so deletion is authorized without preserve-override
    expansion.
    """
    rel = ".claude/hooks/workstream-focus.py"
    _assert_in_isolation_surface(rel)
    legacy_hook = target / rel
    if not legacy_hook.exists():
        return IsolationFixerResult(
            check_name="isolation:workstream-focus-hook-absent",
            file=rel,
            outcome="no-op",
            reason="legacy hook already absent",
            prior_policy=_prior_policy_for(rel),
        )
    legacy_hook.unlink()
    return IsolationFixerResult(
        check_name="isolation:workstream-focus-hook-absent",
        file=rel,
        outcome="fixed",
        reason="deleted deprecated workstream-focus.py per ADR-ISOLATION-APPLICATION-PLACEMENT-001",
        prior_policy=_prior_policy_for(rel),
    )


_RELEASE_READINESS_BANNER = (
    "# Application release-readiness — application subject\n\n"
    "_This file is the application's release-readiness record. Header asserts "
    "application subject per Phase 9 §4 lines 217–218. Do not combine GT-KB "
    "(platform) status with application status._\n"
)


def _fix_isolation_release_readiness_banner(target: Path) -> IsolationFixerResult:
    """Rewrite the first non-blank line of memory/release-readiness.md to assert application subject.

    Per check #8 (``isolation:release-readiness-app-subject-header``). The
    doctor check fails when the first non-blank line does not mention
    "application" or when GT-KB subject is combined with green keywords.
    """
    rel = "memory/release-readiness.md"
    _assert_in_isolation_surface(rel)
    rr_path = target / rel
    if not rr_path.exists():
        # Create with the canonical banner.
        rr_path.parent.mkdir(parents=True, exist_ok=True)
        rr_path.write_text(_RELEASE_READINESS_BANNER, encoding="utf-8")
        return IsolationFixerResult(
            check_name="isolation:release-readiness-app-subject-header",
            file=rel,
            outcome="fixed",
            reason="created release-readiness.md with application-subject banner",
            prior_policy=_prior_policy_for(rel),
        )
    text = rr_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=False)
    # Find first non-blank line index.
    first_idx = next((i for i, ln in enumerate(lines) if ln.strip()), -1)
    canonical_header = "# Application release-readiness — application subject"
    if first_idx >= 0 and lines[first_idx].strip() == canonical_header:
        return IsolationFixerResult(
            check_name="isolation:release-readiness-app-subject-header",
            file=rel,
            outcome="no-op",
            reason="header already asserts application subject",
            prior_policy=_prior_policy_for(rel),
        )
    if first_idx >= 0:
        lines[first_idx] = canonical_header
    else:
        lines = [canonical_header]
    rr_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return IsolationFixerResult(
        check_name="isolation:release-readiness-app-subject-header",
        file=rel,
        outcome="fixed",
        reason=(
            "rewrote first non-blank line to assert application subject; "
            "preserve policy overridden under --accept-migration"
        ),
        prior_policy=_prior_policy_for(rel),
    )


# Single source of truth for the dispatcher mapping. T13 asserts this contains
# exactly the 5 check names in _PARTITION_AUTO_FIXABLE (no missing keys, no
# extras) and that each helper is invoked when its check is dispatched.
_ISOLATION_FIXER_MAP: dict[str, Callable[[Path], IsolationFixerResult]] = {
    "isolation:service-endpoint": _fix_isolation_service_endpoint,
    "isolation:work-subject": _fix_isolation_work_subject,
    "isolation:workstream-focus-hook-absent": _fix_isolation_remove_workstream_focus_hook,
    "isolation:release-readiness-app-subject-header": _fix_isolation_release_readiness_banner,
}


def _run_isolation_fixers(
    target: Path,
    profile: str,
    auto_fixable_checks: list[ToolCheck],
) -> list[IsolationFixerResult]:
    """Typed dispatcher: invoke the helper for each auto-fixable check.

    Per F1 fix in bridge -005 / -007: isolation fixers are NOT ``UpgradeAction``
    rows; they are a sibling typed code path within ``execute_upgrade()`` that
    runs inside the payload branch.

    Raises:
        RuntimeError: if a check's name has no helper in
            :data:`_ISOLATION_FIXER_MAP` (defensive — partition contract test
            T11 + dispatcher contract test T13 ensure this never fires in
            practice).
    """
    results: list[IsolationFixerResult] = []
    for check in auto_fixable_checks:
        helper = _ISOLATION_FIXER_MAP.get(check.name)
        if helper is None:
            raise RuntimeError(
                f"_ISOLATION_FIXER_MAP missing helper for {check.name!r}; "
                f"this is a partition/dispatcher contract bug. "
                f"Ensure _ISOLATION_FIXER_MAP keys equal _PARTITION_AUTO_FIXABLE."
            )
        results.append(helper(target))
    return results


@dataclass
class UpgradeAction:
    """A single file or config action in the upgrade plan.

    ``payload`` is used by non-file-copy action types (``merge-event-hooks``
    and ``append-gitignore``) to carry event or pattern metadata. File-copy
    actions (``update``, ``add``, ``skip``) ignore it and the default
    empty-string preserves every existing three-argument call site and test.

    ``event`` identifies the settings hook event (``PreToolUse``,
    ``UserPromptSubmit``, ``PostToolUse``, ``SessionStart``, ``Stop``, etc.)
    for ``merge-event-hooks`` actions. Defaults to ``"PreToolUse"`` for
    back-compat with any call site or test that constructs an
    ``UpgradeAction`` without explicitly naming the field; canonical
    planner emissions always set it explicitly.

    ``warning`` and ``informational`` are **non-mutating pre-flight rows**
    produced by :mod:`groundtruth_kb.project.preflight` (bridge C2). The
    CLI filters them out of the list passed to :func:`execute_upgrade` so
    git/manifest work never runs on a warning-only plan, regardless of
    ``--force``. Per bridge ``gtkb-upgrade-pre-flight-checks-implementation-002.md``
    condition C1.
    """

    file: str
    action: Literal[
        "update",
        "add",
        "skip",
        "merge-event-hooks",
        "append-gitignore",
        "warning",
        "informational",
    ]
    reason: str
    payload: str = ""
    event: str = "PreToolUse"


# Action kinds that represent non-mutating pre-flight diagnostics. The CLI
# filters these out of the action list passed to :func:`execute_upgrade` so
# pre-flight reporting never triggers git, manifest, or file mutation —
# even with ``--force``. Per C1 of
# ``bridge/gtkb-upgrade-pre-flight-checks-implementation-002.md``.
_NON_MUTATING_ACTION_KINDS: frozenset[str] = frozenset({"warning", "informational"})


def _file_hash(path: Path) -> str:
    """SHA-256 of a file's content."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _template_hash(template_relative: str) -> str | None:
    """SHA-256 of the bundled template file."""
    templates = get_templates_dir()
    path = templates / template_relative
    if path.exists():
        return _file_hash(path)
    return None


def _ownership_permits_upgrade_action(artifact: FileArtifact | SettingsHookRegistration | GitignorePattern) -> bool:
    """Return True iff *artifact*'s ownership policy allows an upgrade action.

    Per the artifact-ownership matrix (``OwnershipResolver``), rows whose
    ``upgrade_policy`` is one of ``preserve`` / ``transient`` /
    ``adopter-opt-in`` do not produce any upgrade-time action. All 40
    current-HEAD registry rows have ``overwrite`` or ``structured-merge``
    policies, so this filter is a no-op on the existing registry and
    preserves bit-identical upgrade behavior.
    """
    meta = artifact.ownership
    if meta is None:
        # Loader guarantees ownership metadata is always populated for
        # non-ownership-glob rows; bail defensively to original behavior.
        return True
    return meta.upgrade_policy not in _NO_UPGRADE_ACTION_POLICIES


def _managed_file_artifacts(profile_name: str, class_: str) -> list[FileArtifact]:
    """Return every :class:`FileArtifact` of *class_* managed for *profile_name*.

    Thin typed adapter over ``artifacts_for_upgrade`` that narrows the
    union type to :class:`FileArtifact` for mypy. Filters out rows whose
    ownership policy forbids an upgrade-time action (preserve / transient /
    adopter-opt-in); preserves current behavior for all 40 existing rows
    because they all use ``overwrite`` or ``structured-merge``.
    """
    raw = artifacts_for_upgrade(profile_name, class_=class_)  # type: ignore[arg-type]
    return [a for a in raw if isinstance(a, FileArtifact) and _ownership_permits_upgrade_action(a)]


def _managed_settings_registrations(profile_name: str) -> list[SettingsHookRegistration]:
    """Return every :class:`SettingsHookRegistration` managed for *profile_name*."""
    raw = artifacts_for_upgrade(profile_name, class_="settings-hook-registration")
    return [a for a in raw if isinstance(a, SettingsHookRegistration) and _ownership_permits_upgrade_action(a)]


def _managed_gitignore_patterns(profile_name: str) -> list[GitignorePattern]:
    """Return every :class:`GitignorePattern` managed for *profile_name*."""
    raw = artifacts_for_upgrade(profile_name, class_="gitignore-pattern")
    return [a for a in raw if isinstance(a, GitignorePattern) and _ownership_permits_upgrade_action(a)]


def _plan_missing_managed_files(target: Path, profile_name: str) -> list[UpgradeAction]:
    """Plan ``add`` actions for any missing managed hook/rule/skill file.

    Runs unconditionally (not version-gated) so a missing managed file
    at the current scaffold version still produces a repair action.
    Addresses the same-version inert-hook drift flagged in
    ``bridge/gtkb-hook-scanner-safe-writer-010.md`` Finding 1, the
    same-version missing-skill drift flagged in
    ``bridge/gtkb-skill-decision-capture-009.md`` Finding 1, and Gap 2.8
    (bridge rules missing repair) flagged in the non-disruptive upgrade
    investigation.
    """
    actions: list[UpgradeAction] = []
    for class_ in ("hook", "rule", "skill"):
        for artifact in _managed_file_artifacts(profile_name, class_):
            project_path = target / artifact.target_path
            if project_path.exists():
                continue
            if _template_hash(artifact.template_path) is None:
                continue
            actions.append(
                UpgradeAction(
                    file=artifact.target_path,
                    action="add",
                    reason="Managed file missing — will copy from template",
                )
            )
    return actions


def _plan_managed_file_drift(
    target: Path,
    profile_name: str,
    class_: str,
) -> list[UpgradeAction]:
    """Plan ``skip`` actions for managed files of *class_* that differ from template.

    Missing-file case is handled by :func:`_plan_missing_managed_files`.
    """
    actions: list[UpgradeAction] = []
    for artifact in _managed_file_artifacts(profile_name, class_):
        project_path = target / artifact.target_path
        if not project_path.exists():
            continue  # Missing-file case handled elsewhere.

        template_h = _template_hash(artifact.template_path)
        if template_h is None:
            continue

        project_h = _file_hash(project_path)
        if project_h == template_h:
            continue

        actions.append(
            UpgradeAction(
                file=artifact.target_path,
                action="skip",
                reason="File differs from template (customized?) — use --force to overwrite",
            )
        )
    return actions


def _map_target_to_template(target_path: str) -> str | None:
    """Map a managed target path back to its template-relative source.

    Used by :func:`execute_upgrade` to locate the template bytes to copy.
    Uses the registry as the lookup table rather than hardcoded path
    prefix heuristics.
    """
    from groundtruth_kb.project.managed_registry import _load_all_artifacts

    for artifact in _load_all_artifacts():
        if isinstance(artifact, FileArtifact) and artifact.target_path == target_path:
            return artifact.template_path
    return None


def _entry_commands(entry: object) -> list[str]:
    """Extract every ``command`` string reachable from a hooks event entry."""
    if not isinstance(entry, dict):
        return []
    entry_hooks = entry.get("hooks", [])
    if not isinstance(entry_hooks, list):
        return []
    out: list[str] = []
    for h in entry_hooks:
        if isinstance(h, dict):
            cmd = h.get("command", "")
            if isinstance(cmd, str):
                out.append(cmd)
    return out


def _compute_target_event_list(
    existing_entries: list[object],
    scaffold_registrations: list[SettingsHookRegistration],
) -> tuple[list[object], int, int]:
    """Return ``(target_list, n_managed, n_preserved)``.

    The target list is the registry-ordered managed block followed by the
    unmanaged block in original relative order. Existing managed entries
    are reused by identity when their command marker matches; missing
    managed entries are synthesized in the canonical shape. Duplicate
    managed entries collapse to the first occurrence. Non-dict entries and
    entries whose commands do not match any scaffold-superset marker fall
    into the unmanaged block.

    This helper is the SINGLE definition of "target list" shared by
    :func:`_plan_settings_registration` and
    :func:`_execute_merge_event_hooks`; both route through it so planner
    and apply agree by construction.
    """
    scaffold_filenames: list[str] = [r.hook_filename for r in scaffold_registrations]
    scaffold_markers: set[str] = {f"python .claude/hooks/{fn}" for fn in scaffold_filenames}

    managed_existing_by_marker: dict[str, object] = {}
    unmanaged: list[object] = []
    for entry in existing_entries:
        matched_marker: str | None = None
        for cmd in _entry_commands(entry):
            for marker in scaffold_markers:
                if marker in cmd:
                    matched_marker = marker
                    break
            if matched_marker is not None:
                break
        if matched_marker is None:
            unmanaged.append(entry)
        else:
            managed_existing_by_marker.setdefault(matched_marker, entry)

    new_managed_block: list[object] = []
    for filename in scaffold_filenames:
        marker = f"python .claude/hooks/{filename}"
        reused = managed_existing_by_marker.get(marker)
        if isinstance(reused, dict):
            new_managed_block.append(reused)
        else:
            new_managed_block.append({"hooks": [{"type": "command", "command": marker}]})

    target_list: list[object] = [*new_managed_block, *unmanaged]
    return target_list, len(new_managed_block), len(unmanaged)


def _plan_settings_registration(target: Path, profile_name: str) -> list[UpgradeAction]:
    """Plan structured-merge actions for settings hook events.

    For each event that contains any upgrade-enforced
    ``settings-hook-registration`` record, computes the target event list
    (registry-ordered managed block ++ unmanaged block in original relative
    order) via :func:`_compute_target_event_list`. Emits a
    ``merge-event-hooks`` action iff the target list differs from the
    existing list. Planner and :func:`_execute_merge_event_hooks` share
    this helper, so planner emits an action iff apply would change the
    file.

    Defensive against malformed shapes:

    - If ``settings.json`` is absent: return ``[]`` (non-Claude-Code project).
    - If the file is unreadable: return ``[]`` (can't plan without reading).
    - If the JSON parse fails: emit a single ``skip`` action with a
      manual-repair reason.
    - If the root is not a dict, ``hooks`` is not a dict, or
      ``hooks[event]`` is not a list: treat as empty existing entries.
    """
    settings_path = target / ".claude" / "settings.json"
    if not settings_path.exists():
        return []

    try:
        data: object = json.loads(settings_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return [
            UpgradeAction(
                file=".claude/settings.json",
                action="skip",
                reason="Malformed JSON — manual repair required",
            )
        ]
    except OSError:
        return []

    if not isinstance(data, dict):
        hooks_dict: dict[str, object] = {}
    else:
        raw_hooks = data.get("hooks", {})
        hooks_dict = raw_hooks if isinstance(raw_hooks, dict) else {}

    from groundtruth_kb.project.managed_registry import artifacts_for_scaffold

    # Partition scaffold-superset registrations by event in registry order.
    scaffold_by_event: dict[str, list[SettingsHookRegistration]] = {}
    scaffold_raw = artifacts_for_scaffold(profile_name, class_="settings-hook-registration")
    for artifact in scaffold_raw:
        if isinstance(artifact, SettingsHookRegistration):
            scaffold_by_event.setdefault(artifact.event, []).append(artifact)

    # Outer-loop key set: every event that contains at least one
    # upgrade-enforced record for the active profile. A merge only fires
    # against events the registry claims ownership of.
    upgrade_enforced_by_event: dict[str, list[SettingsHookRegistration]] = {}
    for registration in _managed_settings_registrations(profile_name):
        upgrade_enforced_by_event.setdefault(registration.event, []).append(registration)

    actions: list[UpgradeAction] = []
    for event in upgrade_enforced_by_event:
        raw_event_entries = hooks_dict.get(event)
        event_entries: list[object] = raw_event_entries if isinstance(raw_event_entries, list) else []

        scaffold_registrations = scaffold_by_event.get(event, [])
        target_event_list, _n_managed, _n_preserved = _compute_target_event_list(event_entries, scaffold_registrations)

        # Trigger: merge is required iff the target list apply would produce
        # differs from the existing list. This captures every mismatch shape
        # — missing managed entries, wrong managed order, interleaved
        # unmanaged entries, non-list existing value, and duplicate
        # collapses — without a per-shape check.
        if target_event_list != event_entries:
            actions.append(
                UpgradeAction(
                    file=".claude/settings.json",
                    action="merge-event-hooks",
                    reason=f"Merge {event} hooks to registry order",
                    payload=event,
                    event=event,
                )
            )

    return actions


def _plan_gitignore_patterns(target: Path, profile_name: str) -> list[UpgradeAction]:
    """Plan ``.gitignore`` pattern additions.

    Emits ``append-gitignore`` actions for patterns NOT already present in
    ``.gitignore``. If ``.gitignore`` is absent, emits one
    ``append-gitignore`` action per applicable pattern — the execute step
    creates the file.
    """
    gitignore = target / ".gitignore"
    existing = ""
    if gitignore.exists():
        try:
            existing = gitignore.read_text(encoding="utf-8")
        except OSError:
            return []

    existing_lines = {line.strip() for line in existing.splitlines()}

    actions: list[UpgradeAction] = []
    for pattern_record in _managed_gitignore_patterns(profile_name):
        if pattern_record.pattern in existing_lines:
            continue
        actions.append(
            UpgradeAction(
                file=".gitignore",
                action="append-gitignore",
                reason=f"Append pattern: {pattern_record.pattern} ({pattern_record.comment})",
                payload=pattern_record.pattern,
            )
        )
    return actions


# ---------------------------------------------------------------------------
# Rollback-receipts integration (Phase 3 of bridge gtkb-rollback-receipts-014)
# ---------------------------------------------------------------------------
#
# ``execute_upgrade`` runs the adopter's planned actions inside a short-lived
# payload branch that merges back into the target branch with ``--no-ff``.
# The resulting merge commit is what a future ``gt project rollback`` can
# target with ``git revert -m 1 <merge_commit>``. The rollback receipt is
# written AFTER the merge commit exists so its ``merge_commit`` field records
# the real SHA, and — in tracked mode — the receipt lands in a SEPARATE
# post-merge commit that is not part of the payload merge tree.
#
# Authorizing bridge: ``bridge/gtkb-rollback-receipts-014.md`` (Codex GO).


class MalformedSettingsError(RuntimeError):
    """Raised when ``execute_upgrade`` sees a malformed-settings skip in the action list.

    ``plan_upgrade`` still emits a ``skip`` action with reason starting
    ``"Malformed JSON"`` so ``--dry-run`` surfaces the problem; ``--apply``
    must refuse before any git checkout or file write. The adopter repairs
    ``.claude/settings.json`` manually and re-runs.

    Per bridge ``gtkb-upgrade-pre-flight-checks-implementation-002.md`` C2.
    """

    def __init__(self, action: UpgradeAction) -> None:
        super().__init__(
            f"Cannot upgrade: {action.file} has malformed JSON. "
            f"Repair manually and re-run. Planner reason: {action.reason}"
        )
        self.action = action


def _has_malformed_settings_skip(actions: list[UpgradeAction]) -> UpgradeAction | None:
    """Return the first malformed-settings ``skip`` action in *actions*, or ``None``.

    Used by :func:`execute_upgrade` to halt before any git or file work
    when the planner signaled that ``.claude/settings.json`` is malformed,
    and by the CLI for the same halt at the process boundary (defense in
    depth).
    """
    for action in actions:
        if (
            action.action == "skip"
            and action.file == ".claude/settings.json"
            and action.reason.startswith("Malformed JSON")
        ):
            return action
    return None


class NotAGitRepositoryError(RuntimeError):
    """Raised when ``execute_upgrade`` is invoked outside a git work tree.

    The payload-branch-and-merge flow requires git. Adopters who were
    previously running ``gt project upgrade`` without a git repo must
    initialize one and commit their current state before upgrading.
    """

    def __init__(self, target: Path) -> None:
        super().__init__(
            f"{target} is not inside a git work tree. "
            "`gt project upgrade --apply` now requires git so it can record "
            "a rollback receipt. Run `git init && git add -A && git commit -m 'pre-upgrade snapshot'` first."
        )
        self.target = target


class DirtyWorkingTreeError(RuntimeError):
    """Raised when the target has uncommitted changes at upgrade time.

    A dirty tree would cause unrelated adopter work to be rolled into the
    payload commit, which defeats the rollback contract. The adopter must
    commit or stash first.
    """

    def __init__(self, target: Path, status: str) -> None:
        super().__init__(
            f"Working tree at {target} has uncommitted changes; commit or stash "
            f"before running `gt project upgrade --apply`.\ngit status --porcelain:\n{status}"
        )
        self.target = target
        self.status = status


class MergeFailedError(RuntimeError):
    """Raised when ``git merge --no-ff`` of the payload branch fails.

    Typical causes: conflicts between the payload and newer commits on the
    target branch (rare at upgrade time since we required a clean tree),
    or an environmental git failure. The caller is responsible for leaving
    the repository in a usable state.
    """

    def __init__(self, stdout: str, stderr: str) -> None:
        super().__init__(f"git merge --no-ff of upgrade payload failed.\nstdout:\n{stdout}\nstderr:\n{stderr}")
        self.stdout = stdout
        self.stderr = stderr


# Path prefix → managed artifact class. Used by ``_artifact_classes_touched``
# to derive the ``artifact_classes_touched`` field of the rollback receipt
# from the applied actions without re-reading the registry.
_FILE_CLASS_PREFIXES: tuple[tuple[str, str], ...] = (
    (".claude/hooks/", "hook"),
    (".claude/rules/", "rule"),
    (".claude/skills/", "skill"),
)


def _run_git(
    target: Path,
    *args: str,
    check: bool = True,
    capture: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Run ``git *args`` in ``target``. Text mode, optional capture."""
    return subprocess.run(
        ["git", *args],
        cwd=str(target),
        check=check,
        capture_output=capture,
        text=True,
    )


def _require_git_repo(target: Path) -> None:
    """Raise :class:`NotAGitRepositoryError` unless ``target`` is a git work tree."""
    result = _run_git(target, "rev-parse", "--is-inside-work-tree", check=False)
    if result.returncode != 0 or result.stdout.strip() != "true":
        raise NotAGitRepositoryError(target)


def _require_clean_tree(target: Path) -> None:
    """Raise :class:`DirtyWorkingTreeError` if ``target`` has uncommitted changes."""
    result = _run_git(target, "status", "--porcelain")
    if result.stdout.strip():
        raise DirtyWorkingTreeError(target, result.stdout)


def _current_branch(target: Path) -> str:
    """Return the short name of ``HEAD``'s current branch (e.g. ``"main"``)."""
    return _run_git(target, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()


def _commit_payload(target: Path, message: str) -> str | None:
    """Stage and commit everything on the current branch.

    Returns the new commit SHA, or ``None`` if there was nothing to commit.
    The latter signals a no-op upgrade (all actions were ``skip`` and the
    manifest was already at ``__version__``), in which case the caller
    should abort the merge and receipt flow cleanly.
    """
    _run_git(target, "add", "-A")
    status = _run_git(target, "status", "--porcelain").stdout.strip()
    if not status:
        return None
    _run_git(target, "commit", "-m", message)
    return _run_git(target, "rev-parse", "HEAD").stdout.strip()


def _merge_payload(
    target: Path,
    target_branch: str,
    payload_branch: str,
    message: str,
) -> str:
    """Switch to ``target_branch`` and ``git merge --no-ff`` the payload branch.

    Returns the resulting merge commit SHA. Raises :class:`MergeFailedError`
    if the merge itself fails (conflicts or git error); the caller's
    ``finally`` block is responsible for payload-branch cleanup.
    """
    _run_git(target, "checkout", target_branch)
    result = _run_git(
        target,
        "merge",
        "--no-ff",
        payload_branch,
        "-m",
        message,
        check=False,
    )
    if result.returncode != 0:
        raise MergeFailedError(result.stdout, result.stderr)
    return _run_git(target, "rev-parse", "HEAD").stdout.strip()


def _cleanup_payload_branch(target: Path, payload_branch: str) -> None:
    """Best-effort ``git branch -D <payload_branch>``.

    Runs with ``check=False`` so cleanup failures do not mask the original
    error in the caller's ``finally`` block. After a successful merge the
    payload branch is reachable from the merge commit, so ``-D`` is safe.
    """
    _run_git(target, "branch", "-D", payload_branch, check=False)


def _artifact_classes_touched(actions: list[UpgradeAction]) -> list[str]:
    """Return the sorted set of artifact classes actually modified by *actions*.

    Recorded in the rollback receipt as ``artifact_classes_touched`` so a
    future rollback tool can report which subsystems the upgrade had
    touched without re-parsing the payload commit. ``skip`` actions are
    excluded (they don't mutate anything).
    """
    seen: set[str] = set()
    for action in actions:
        if action.action == "merge-event-hooks":
            seen.add("settings-hook-registration")
        elif action.action == "append-gitignore":
            seen.add("gitignore-pattern")
        elif action.action in ("update", "add"):
            for prefix, class_ in _FILE_CLASS_PREFIXES:
                if action.file.startswith(prefix):
                    seen.add(class_)
                    break
    return sorted(seen)


def plan_upgrade(target: Path, *, ignore_inflight_bridges: bool = False) -> list[UpgradeAction]:
    """Plan the upgrade: pre-flight diagnostics + managed-file updates + config drift repairs.

    Always runs settings and gitignore drift checks so that config drift is
    repaired even when the scaffold version is already current. Managed
    hook/rule/skill file updates remain gated on
    ``scaffold_version != __version__`` to avoid unnecessary re-copy of
    unchanged files.

    Pre-flight diagnostics (bridge
    ``gtkb-upgrade-pre-flight-checks-implementation-002.md``) run before
    the drift checks and emit non-mutating ``warning`` / ``informational``
    actions. The CLI filters those out of the list passed to
    :func:`execute_upgrade` so pre-flight reporting never triggers git or
    file writes.

    Args:
        target: Adopter project root.
        ignore_inflight_bridges: When True, suppresses the 5.2 bridge
            in-flight warnings. Used by automation / CI that can't be
            paused by active bridge review.
    """
    manifest = read_manifest(target / "groundtruth.toml")
    if manifest is None:
        return [
            UpgradeAction(
                file="groundtruth.toml",
                action="skip",
                reason="No [project] manifest found — run `gt project init` first",
            )
        ]

    profile = get_profile(manifest.profile)
    actions: list[UpgradeAction] = []

    # Pre-flight checks (Area 5.2 + 5.6) — emit non-mutating diagnostic
    # rows that the CLI displays but never passes to ``execute_upgrade``.
    # 5.3 halt (malformed settings) is inherited from the existing
    # ``_plan_settings_registration`` skip-action emission below + the
    # ``execute_upgrade`` pre-pre-flight scan for ``MalformedSettingsError``.
    from groundtruth_kb.project.preflight import (
        _check_bridge_inflight,
        _check_isolation_state,
        _check_scaffold_coverage,
    )

    actions.extend(_check_bridge_inflight(target, ignore=ignore_inflight_bridges))
    actions.extend(_check_scaffold_coverage(target, profile.name))
    # GTKB-ISOLATION-017 Slice 4: surface isolation-doctor failures as
    # non-mutating diagnostic rows so dry-run reports show them. The CLI
    # filters warning/informational rows out before execute_upgrade so these
    # never trigger git or file mutation. The actual gating + auto-fix
    # invocation happens in execute_upgrade via _run_isolation_preflight +
    # _run_isolation_fixers.
    actions.extend(_check_isolation_state(target, profile.name))

    # Drift checks run unconditionally (even at current scaffold version)
    # so that missing managed files, missing PreToolUse registrations,
    # and missing gitignore patterns are always surfaced by
    # ``gt project upgrade --dry-run``.
    actions.extend(_plan_missing_managed_files(target, profile.name))
    actions.extend(_plan_settings_registration(target, profile.name))
    actions.extend(_plan_gitignore_patterns(target, profile.name))

    # Managed-file hash/customization checks are gated on version change —
    # at the current version, files present on disk are assumed to match
    # the template (or be intentional customizations). Missing files are
    # already handled above.
    if manifest.scaffold_version != __version__:
        for class_ in ("hook", "rule", "skill"):
            actions.extend(_plan_managed_file_drift(target, profile.name, class_))

    return actions


def execute_upgrade(
    target: Path,
    actions: list[UpgradeAction],
    *,
    force: bool = False,
    accept_migration: bool = False,
    product_root: Path | None = None,
    enforce_isolation: bool = True,
    update_manifest: bool = True,
) -> list[str]:
    """Execute planned upgrade actions via a payload-branch-and-merge flow.

    The flow (per ``bridge/gtkb-rollback-receipts-014.md`` GO + bridge
    ``gtkb-isolation-017-slice4-upgrade-2026-05-02-008.md`` GO):

    1. Pre-pre-flight: malformed-settings halt + GTKB-ISOLATION-017 isolation
       gating (per Slice 4). Hard-refuse on adopter-root-placement violations
       regardless of ``accept_migration``. Refuse on any failing isolation
       check unless ``accept_migration=True``. Refuse on needs-adopter-input
       checks even when ``accept_migration=True``.
    2. Pre-flight: verify git work tree + clean tree; resolve receipt mode.
    3. Create and switch to a short-lived ``gt-upgrade-payload-<id>`` branch.
    4. Run isolation auto-fixers (Slice 4) — only when ``accept_migration=True``
       AND the auto-fixable partition is non-empty. Fixer outcomes recorded
       in the rollback receipt's ``isolation_migration`` block.
    5. Apply file actions on the payload branch (existing flow).
    6. Commit the payload, merge with ``--no-ff``, write rollback receipt.

    Args:
        target: Adopter project root.
        force: Overwrite customized files (passes through to file-action executor).
        accept_migration: Slice 4 — explicit opt-in to one-shot isolation
            migration. Required to run isolation auto-fixers; without it,
            isolation failures cause refusal. Per
            ``DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE``.
        product_root: Slice 4 — GT-KB product root for isolation pre-flight
            (used to detect adopter-under-product-root placement violation).
            Defaults to ``Path(__file__).resolve().parents[3]`` when not set.
        update_manifest: Per bridge ``gtkb-scaffold-upgrade-tier-a-009.md``
            GO. Defaults True to preserve current behavior. When False,
            the ``manifest.scaffold_version`` write inside
            ``_apply_file_actions`` is skipped so ``groundtruth.toml`` is not
            mutated. Callers that apply a partial action set (e.g. Tier A
            pure-ADDs + APPEND-GITIGNORE) use ``update_manifest=False`` to
            keep deferred ``SKIP`` rows visible in subsequent
            ``plan_upgrade()`` calls. Aligns with
            ``DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE``.

    Raises:
        MalformedSettingsError: malformed ``.claude/settings.json``.
        IsolationLocationFailureError: adopter root under product root (check #1).
        IsolationMigrationRequiredError: isolation checks fail and ``accept_migration`` not set.
        IsolationNonAutoFixableError: needs-adopter-input checks fail with ``accept_migration`` set.
        NotAGitRepositoryError: ``target`` is not inside a git work tree.
        DirtyWorkingTreeError: uncommitted changes present before upgrade.
        MergeFailedError: ``git merge --no-ff`` of the payload failed.
    """
    # Pre-pre-flight: malformed-settings halt (C2). Must run BEFORE any git
    # precondition or branch creation so ``--apply`` refuses cleanly and the
    # adopter repairs settings.json without mixed state.
    malformed = _has_malformed_settings_skip(actions)
    if malformed is not None:
        raise MalformedSettingsError(malformed)

    # Slice 4: isolation pre-flight + gating. Runs BEFORE git checks so refusal
    # paths surface cleanly without leaving the adopter in mixed state.
    # ``enforce_isolation`` defaults True (production CLI path); library callers
    # that want the pre-Slice-4 plain-executor semantics can pass False (e.g.,
    # pre-existing test fixtures that don't model an isolation-clean adopter).
    isolation_result: IsolationPreflightResult = IsolationPreflightResult()
    profile_name_for_iso = "dual-agent"
    if enforce_isolation:
        if product_root is None:
            # Match doctor.py:_PRODUCT_ROOT computation: parents[3] from this file.
            product_root = Path(__file__).resolve().parents[3]
        manifest_for_profile = read_manifest(target / "groundtruth.toml")
        profile_name_for_iso = manifest_for_profile.profile if manifest_for_profile else "dual-agent"
        isolation_result = _run_isolation_preflight(target, profile_name_for_iso, product_root)
        if isolation_result.hard_refuse:
            raise IsolationLocationFailureError(target, isolation_result.hard_refuse)
        failing = isolation_result.auto_fixable + isolation_result.needs_adopter_input
        if failing and not accept_migration:
            raise IsolationMigrationRequiredError(target, failing)
        if isolation_result.needs_adopter_input and accept_migration:
            raise IsolationNonAutoFixableError(target, isolation_result.needs_adopter_input)

    _require_git_repo(target)
    _require_clean_tree(target)

    manifest = read_manifest(target / "groundtruth.toml")
    if manifest is None:
        return ["SKIPPED — no groundtruth.toml manifest (run `gt project init` first)"]

    from_version = manifest.scaffold_version
    target_branch = _current_branch(target)

    receipt_id = uuid.uuid4().hex[:16]
    receipt_path = target / ".claude" / "upgrade-receipts" / "active" / f"{receipt_id}.json"

    # Pre-flight: resolver reads the adopter's starting .gitignore state,
    # before any upgrade write. ``gt project upgrade --apply`` never mutates
    # .gitignore for receipt-tracking purposes (per -013 condition 3).
    resolved = resolve_receipt_mode(target, receipt_path)

    payload_branch = f"gt-upgrade-payload-{receipt_id}"
    _run_git(target, "checkout", "-b", payload_branch)
    on_payload_branch = True

    try:
        # Slice 4: invoke isolation fixers BEFORE _apply_file_actions so the
        # payload commit captures both the isolation migration AND the routine
        # upgrade actions. Single payload + single receipt + single revert path.
        isolation_fixer_results: list[IsolationFixerResult] = []
        if accept_migration and isolation_result.auto_fixable:
            isolation_fixer_results = _run_isolation_fixers(target, profile_name_for_iso, isolation_result.auto_fixable)
            for fr in isolation_fixer_results:
                tag = "FIXED" if fr.outcome == "fixed" else fr.outcome.upper()
                # Use append rather than prepend; results list ordering is informational.
                # Initial empty list — populated by _apply_file_actions below.
                # Track in a separate buffer; merged into results after _apply.
                pass  # noqa: PIE790

        results = _apply_file_actions(target, actions, force=force, update_manifest=update_manifest)

        # Surface isolation-fixer rows in the result log for adopter visibility.
        for fr in isolation_fixer_results:
            tag = "FIXED" if fr.outcome == "fixed" else fr.outcome.upper()
            results.insert(0, f"[ISOLATION] {tag} {fr.file} ({fr.check_name}) — {fr.reason}")

        payload_commit = _commit_payload(target, f"gt: upgrade payload to {__version__}")
        if payload_commit is None:
            results.append("SKIPPED — no changes to apply")
            _run_git(target, "checkout", target_branch)
            on_payload_branch = False
            return results

        _run_git(target, "checkout", target_branch)
        on_payload_branch = False

        merge_commit = _merge_payload(
            target,
            target_branch,
            payload_branch,
            f"gt: merge upgrade payload to {__version__}",
        )
        results.append(f"MERGED payload into {target_branch} @ {merge_commit[:10]}")

        receipt: ReceiptJSON = {
            "schema_version": "v1",
            "receipt_id": receipt_id,
            "merge_commit": merge_commit,
            "target_branch": target_branch,
            "from_version": from_version,
            "to_version": __version__,
            "mode": resolved.mode,
            "created_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "artifact_classes_touched": _artifact_classes_touched(actions),
        }
        # Slice 4: optional isolation_migration audit block. Only present when
        # accept_migration was set AND fixers ran. Per F2 audit-trail contract.
        if accept_migration and (isolation_fixer_results or isolation_result.auto_fixable):
            receipt["isolation_migration"] = {
                "auto_fixed": [
                    {
                        "check_name": fr.check_name,
                        "file": fr.file,
                        "outcome": fr.outcome,
                        "prior_policy": fr.prior_policy,
                        "reason": fr.reason,
                    }
                    for fr in isolation_fixer_results
                ],
                "left_for_adopter": [
                    {"check_name": c.name, "message": c.message} for c in isolation_result.needs_adopter_input
                ],
                "preserve_override_authority": (
                    "DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE "
                    "+ S328 owner --accept-migration preserve-override authorization"
                ),
            }
        receipt_outcome = write_receipt(resolved, receipt)
        if resolved.mode == "tracked":
            results.append(f"RECEIPT tracked @ {receipt_outcome[:10]} ({resolved.receipt_path.name})")
        else:
            results.append(f"RECEIPT filesystem at {resolved.receipt_path}")
        return results
    finally:
        if on_payload_branch:
            _run_git(target, "checkout", target_branch, check=False)
        _cleanup_payload_branch(target, payload_branch)


def _apply_file_actions(
    target: Path,
    actions: list[UpgradeAction],
    *,
    force: bool = False,
    update_manifest: bool = True,
) -> list[str]:
    """Apply every action in *actions* on the current branch.

    Inner file-writing half of :func:`execute_upgrade`. Runs on the
    short-lived payload branch only. No ``.bak`` backups are created — the
    payload branch commit is the authoritative pre-merge snapshot.

    ``update_manifest`` (per bridge ``gtkb-scaffold-upgrade-tier-a-009.md``
    GO): defaults True to preserve current behavior. When False, the
    ``manifest.scaffold_version = __version__`` write at the end of this
    function is skipped so ``groundtruth.toml`` is not mutated.
    """
    templates = get_templates_dir()
    results: list[str] = []

    for action in actions:
        # Non-mutating pre-flight rows are safe to re-emit as display text
        # regardless of ``--force``. Per C1 of the pre-flight-checks
        # implementation bridge, these must never map to a template, stage
        # a file, or run a git operation. The CLI filters these out before
        # ``execute_upgrade`` is called; this branch is defense in depth
        # for programmatic callers.
        if action.action in _NON_MUTATING_ACTION_KINDS:
            prefix = "WARNING" if action.action == "warning" else "INFORMATIONAL"
            results.append(f"{prefix} {action.file} — {action.reason}")
            continue

        if action.action == "merge-event-hooks":
            results.append(_execute_merge_event_hooks(target, action))
            continue
        if action.action == "append-gitignore":
            results.append(_execute_append_gitignore(target, action))
            continue

        project_path = target / action.file
        template_rel = _map_target_to_template(action.file)

        if action.action == "skip" and not force:
            results.append(f"SKIPPED {action.file} — {action.reason}")
            continue

        if template_rel is None:
            results.append(f"SKIPPED {action.file} — no template mapping")
            continue

        template_path = templates / template_rel
        if not template_path.exists():
            results.append(f"SKIPPED {action.file} — template not found")
            continue

        project_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(template_path, project_path)
        results.append(f"UPDATED {action.file}")

    if update_manifest:
        manifest = read_manifest(target / "groundtruth.toml")
        if manifest:
            manifest.scaffold_version = __version__
            write_manifest(target / "groundtruth.toml", manifest)
            results.append(f"VERSION scaffold_version → {__version__}")

    return results


def _execute_merge_event_hooks(target: Path, action: UpgradeAction) -> str:
    """Rebuild ``hooks[action.event]`` as managed-block ++ unmanaged-block.

    The managed block is registry-ordered scaffold-superset entries; the
    unmanaged block is every pre-existing entry whose command does not match
    any scaffold-superset marker, preserved in original relative order.
    Shares the :func:`_compute_target_event_list` helper with the planner,
    so apply writes the same list the planner's trigger compared against.
    Idempotent: re-running after a successful merge returns ``SKIPPED``
    because the target list equals the existing list.
    """
    from groundtruth_kb.project.managed_registry import artifacts_for_scaffold
    from groundtruth_kb.project.manifest import read_manifest

    settings_path = target / ".claude" / "settings.json"
    if not settings_path.exists():
        return f"SKIPPED {action.file} — settings.json not found"

    try:
        data: object = json.loads(settings_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return f"SKIPPED {action.file} — malformed JSON"
    except OSError as exc:
        return f"SKIPPED {action.file} — unreadable ({exc})"

    if not isinstance(data, dict):
        return f"SKIPPED {action.file} — settings root is not a JSON object"

    raw_hooks = data.get("hooks")
    if not isinstance(raw_hooks, dict):
        data["hooks"] = {}
    hooks_dict = data["hooks"]

    event = action.event
    manifest = read_manifest(target / "groundtruth.toml")
    profile_name = manifest.profile if manifest else "dual-agent"

    scaffold_raw = artifacts_for_scaffold(profile_name, class_="settings-hook-registration")
    scaffold_registrations: list[SettingsHookRegistration] = [
        a for a in scaffold_raw if isinstance(a, SettingsHookRegistration) and a.event == event
    ]

    raw_existing = hooks_dict.get(event)
    existing_entries: list[object] = raw_existing if isinstance(raw_existing, list) else []

    new_event_list, n_managed, n_preserved = _compute_target_event_list(existing_entries, scaffold_registrations)

    if new_event_list == existing_entries:
        return f"SKIPPED {action.file} — {event} already at registry order"

    hooks_dict[event] = new_event_list
    data["hooks"] = hooks_dict
    try:
        settings_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    except OSError as exc:
        return f"SKIPPED {action.file} — write failed ({exc})"
    return f"MERGED {action.file} — {event} rebuilt ({n_managed} managed, {n_preserved} preserved)"


def _execute_append_gitignore(target: Path, action: UpgradeAction) -> str:
    """Append ``action.payload`` as a pattern to ``.gitignore``.

    Creates the file if absent. Idempotent: no-op if the pattern is already
    present (on its own line, stripped).
    """
    gitignore = target / ".gitignore"
    pattern = action.payload
    if gitignore.exists():
        try:
            content = gitignore.read_text(encoding="utf-8")
        except OSError as exc:
            return f"SKIPPED {action.file} — unreadable ({exc})"
        if any(line.strip() == pattern for line in content.splitlines()):
            return f"SKIPPED {action.file} — pattern {pattern} already present"
        if content and not content.endswith("\n"):
            content += "\n"
        content += f"\n# {action.reason}\n{pattern}\n"
        try:
            gitignore.write_text(content, encoding="utf-8")
        except OSError as exc:
            return f"SKIPPED {action.file} — write failed ({exc})"
    else:
        try:
            gitignore.write_text(f"# {action.reason}\n{pattern}\n", encoding="utf-8")
        except OSError as exc:
            return f"SKIPPED {action.file} — write failed ({exc})"
    return f"APPENDED {pattern} to {action.file}"
