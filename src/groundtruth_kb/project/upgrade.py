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
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from groundtruth_kb import __version__, get_templates_dir
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
        _check_scaffold_coverage,
    )

    actions.extend(_check_bridge_inflight(target, ignore=ignore_inflight_bridges))
    actions.extend(_check_scaffold_coverage(target, profile.name))

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
) -> list[str]:
    """Execute planned upgrade actions via a payload-branch-and-merge flow.

    The flow (per ``bridge/gtkb-rollback-receipts-014.md`` GO):

    1. Pre-flight: verify git work tree + clean tree; resolve receipt mode
       from the adopter's current ``.gitignore`` state.
    2. Create and switch to a short-lived ``gt-upgrade-payload-<id>`` branch.
    3. Apply file actions on the payload branch (NO ``.bak`` backups — git
       history is the audit trail).
    4. Commit the payload. If nothing changed, abort cleanly without a
       merge or receipt.
    5. Switch back to the target branch and ``git merge --no-ff`` the
       payload branch, producing a real merge commit.
    6. Write the rollback receipt post-merge. In tracked mode the receipt
       lands in a SEPARATE post-merge commit at HEAD; the merge commit is
       at HEAD~1 and its tree does not contain the receipt, so
       ``git revert -m 1 <merge_commit>`` rolls back only the payload.

    Raises:
        MalformedSettingsError: the plan contains a malformed-settings skip
            action (``.claude/settings.json`` is not valid JSON); refused
            before any git or file work runs.
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
        results = _apply_file_actions(target, actions, force=force)

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
) -> list[str]:
    """Apply every action in *actions* on the current branch.

    Inner file-writing half of :func:`execute_upgrade`. Runs on the
    short-lived payload branch only. No ``.bak`` backups are created — the
    payload branch commit is the authoritative pre-merge snapshot.
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
