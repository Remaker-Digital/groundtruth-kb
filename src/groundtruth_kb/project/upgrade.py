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
from dataclasses import dataclass
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

    ``payload`` is used by non-file-copy action types (``register-hook`` and
    ``append-gitignore``) to carry the hook filename or gitignore pattern to
    write. File-copy actions (``update``, ``add``, ``skip``) ignore it and
    the default empty-string preserves every existing three-argument call
    site and test.
    """

    file: str
    action: Literal["update", "add", "skip", "register-hook", "append-gitignore"]
    reason: str
    payload: str = ""


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


def _plan_settings_registration(target: Path, profile_name: str) -> list[UpgradeAction]:
    """Plan PreToolUse registrations for managed hooks in ``settings.json``.

    Emits ``register-hook`` actions for settings-hook-registration
    artifacts that are NOT already registered in ``.claude/settings.json``.

    Defensive against malformed shapes:

    - If ``settings.json`` is absent: return ``[]`` (non-Claude-Code project).
    - If the file is unreadable: return ``[]`` (can't plan without reading).
    - If the JSON parse fails: emit a single ``skip`` action with a
      manual-repair reason.
    - If the root is not a dict, ``hooks`` is not a dict, or ``PreToolUse``
      is not a list: treat as empty (no registrations exist, so every
      managed hook must be registered).
    - Entries that are not dicts, or whose ``hooks`` is not a list, are
      ignored while scanning for existing registrations.
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

    # Defensive unwrap: accept malformed shapes without crashing.
    if not isinstance(data, dict):
        hooks_dict: dict[str, object] = {}
    else:
        raw_hooks = data.get("hooks", {})
        hooks_dict = raw_hooks if isinstance(raw_hooks, dict) else {}

    raw_pretooluse = hooks_dict.get("PreToolUse", [])
    pretooluse: list[object] = raw_pretooluse if isinstance(raw_pretooluse, list) else []

    registered_commands: set[str] = set()
    for entry in pretooluse:
        if not isinstance(entry, dict):
            continue
        entry_hooks = entry.get("hooks", [])
        if not isinstance(entry_hooks, list):
            continue
        for h in entry_hooks:
            if not isinstance(h, dict):
                continue
            cmd = h.get("command", "")
            if isinstance(cmd, str):
                registered_commands.add(cmd)

    actions: list[UpgradeAction] = []
    for registration in _managed_settings_registrations(profile_name):
        # C1 scope: only PreToolUse registrations are upgrade-enforced.
        # Other event classes (SessionStart, UserPromptSubmit, PostToolUse)
        # remain scaffold-only per the registry's managed_profiles = [] for
        # those rows. Upgrade enforcement for those event classes is a
        # deferred settings-merge child bridge.
        if registration.event != "PreToolUse":
            continue
        marker = f"python .claude/hooks/{registration.hook_filename}"
        if any(marker in cmd for cmd in registered_commands):
            continue
        actions.append(
            UpgradeAction(
                file=".claude/settings.json",
                action="register-hook",
                reason=f"Register {registration.hook_filename} as PreToolUse hook",
                payload=registration.hook_filename,
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


def plan_upgrade(target: Path) -> list[UpgradeAction]:
    """Plan the upgrade: managed-file updates + config drift repairs.

    Always runs settings and gitignore drift checks so that config drift is
    repaired even when the scaffold version is already current. Managed
    hook/rule/skill file updates remain gated on
    ``scaffold_version != __version__`` to avoid unnecessary re-copy of
    unchanged files.
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
    """Execute planned upgrade actions. Returns status messages."""
    templates = get_templates_dir()
    results: list[str] = []

    for action in actions:
        # Config actions dispatch first — they don't follow the template-copy path.
        if action.action == "register-hook":
            results.append(_execute_register_hook(target, action))
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

        # Backup existing file
        if project_path.exists():
            backup = project_path.with_suffix(project_path.suffix + ".bak")
            shutil.copy2(project_path, backup)
            results.append(f"BACKUP  {action.file} → {backup.name}")

        # Copy template
        project_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(template_path, project_path)
        results.append(f"UPDATED {action.file}")

    # Update scaffold_version in manifest
    manifest = read_manifest(target / "groundtruth.toml")
    if manifest:
        manifest.scaffold_version = __version__
        write_manifest(target / "groundtruth.toml", manifest)
        results.append(f"VERSION scaffold_version → {__version__}")

    return results


def _execute_register_hook(target: Path, action: UpgradeAction) -> str:
    """Non-destructively register ``action.payload`` as a PreToolUse entry.

    Idempotent: if the hook is already registered (command marker present),
    returns a ``SKIPPED`` status. Preserves every existing entry. Defensive
    against malformed settings shape — in that case returns a ``SKIPPED``
    status rather than crashing.
    """
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

    # Defensive: replace any non-dict hooks value with a fresh dict rather
    # than mutating through an unknown type.
    raw_hooks = data.get("hooks")
    if not isinstance(raw_hooks, dict):
        data["hooks"] = {}
    hooks_dict = data["hooks"]

    raw_pretooluse = hooks_dict.get("PreToolUse")
    if not isinstance(raw_pretooluse, list):
        hooks_dict["PreToolUse"] = []
    pretooluse = hooks_dict["PreToolUse"]

    marker = f"python .claude/hooks/{action.payload}"
    for entry in pretooluse:
        if not isinstance(entry, dict):
            continue
        entry_hooks = entry.get("hooks", [])
        if not isinstance(entry_hooks, list):
            continue
        for h in entry_hooks:
            if isinstance(h, dict):
                cmd = h.get("command", "")
                if isinstance(cmd, str) and marker in cmd:
                    return f"SKIPPED {action.file} — {action.payload} already registered"

    pretooluse.append({"hooks": [{"type": "command", "command": marker}]})
    try:
        settings_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    except OSError as exc:
        return f"SKIPPED {action.file} — write failed ({exc})"
    return f"REGISTERED {action.payload} in {action.file}"


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
