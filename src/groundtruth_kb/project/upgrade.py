# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Project upgrade — ``gt project upgrade`` implementation."""

from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from groundtruth_kb import __version__, get_templates_dir
from groundtruth_kb.project.manifest import read_manifest, write_manifest
from groundtruth_kb.project.profiles import ProjectProfile, get_profile


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


# Files managed by the scaffold (overwritten on upgrade unless customized)
_MANAGED_HOOKS = [
    ".claude/hooks/assertion-check.py",
    ".claude/hooks/spec-classifier.py",
    ".claude/hooks/intake-classifier.py",
    ".claude/hooks/destructive-gate.py",
    ".claude/hooks/credential-scan.py",
    ".claude/hooks/scheduler.py",
    ".claude/hooks/scanner-safe-writer.py",
]
_MANAGED_RULES = [
    ".claude/rules/prime-builder.md",
    ".claude/rules/loyal-opposition.md",
    ".claude/rules/bridge-poller-canonical.md",
    ".claude/rules/prime-bridge-collaboration-protocol.md",
    ".claude/rules/report-depth.md",
]
# Managed skill files shipped with the scaffold. Dual-agent profiles receive
# the full set; base profiles receive none. Subdirectory structure
# (``decision-capture/helpers/...``) is preserved through
# :func:`_map_managed_to_template` via ``removeprefix('.claude/skills/')``.
_MANAGED_SKILLS = [
    ".claude/skills/decision-capture/SKILL.md",
    ".claude/skills/decision-capture/helpers/record_decision.py",
]


# Managed PreToolUse hook registrations for ``.claude/settings.json``.
# Each entry is ``(hook_filename, bridge_profile_only)``. plan_upgrade emits
# a ``register-hook`` action for any entry whose corresponding command
# marker is missing from ``hooks.PreToolUse`` in settings.json.
_MANAGED_SETTINGS_PRETOOLUSE_HOOKS: list[tuple[str, bool]] = [
    ("scanner-safe-writer.py", True),  # bridge-profile only (Tier A #2)
]


# Managed ``.gitignore`` patterns. Each entry is
# ``(pattern, comment, bridge_profile_only)``. plan_upgrade emits an
# ``append-gitignore`` action for any pattern that is not already present.
_MANAGED_GITIGNORE_PATTERNS: list[tuple[str, str, bool]] = [
    (".claude/hooks/*.log", "Operational hook logs", True),
]


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


def _map_managed_to_template(managed: str) -> str | None:
    """Map a managed project file to its template source."""
    if managed.startswith(".claude/hooks/"):
        return "hooks/" + managed.split("/")[-1]
    if managed.startswith(".claude/rules/"):
        return "rules/" + managed.split("/")[-1]
    if managed.startswith(".claude/skills/"):
        # Preserve subdirectory structure for the skills/ tree so that
        # ``.claude/skills/decision-capture/helpers/record_decision.py``
        # maps to ``skills/decision-capture/helpers/record_decision.py``
        # under the templates directory.
        return "skills/" + managed.removeprefix(".claude/skills/")
    return None


def _filter_hooks_for_profile(profile: ProjectProfile) -> list[str]:
    """Return managed hooks applicable to the profile."""
    managed = list(_MANAGED_HOOKS)
    if not profile.includes_bridge:
        managed = [
            h
            for h in managed
            if h.split("/")[-1]
            in {
                "assertion-check.py",
                "spec-classifier.py",
            }
        ]
    return managed


def _filter_rules_for_profile(profile: ProjectProfile) -> list[str]:
    """Return managed rules applicable to the profile."""
    managed_rules = list(_MANAGED_RULES)
    if not profile.includes_bridge:
        managed_rules = [r for r in managed_rules if "prime-builder" in r]
    return managed_rules


def _filter_skills_for_profile(profile: ProjectProfile) -> list[str]:
    """Return managed skills applicable to the profile.

    Phase A ships a single dual-agent-only skill
    (``decision-capture``). Base profiles receive no skills. Parallel
    in shape to :func:`_filter_hooks_for_profile` and
    :func:`_filter_rules_for_profile`.
    """
    if not profile.includes_bridge:
        return []
    return list(_MANAGED_SKILLS)


def _plan_missing_managed_files(target: Path, profile: ProjectProfile) -> list[UpgradeAction]:
    """Plan ``add`` actions for any missing managed hook/rule/skill file.

    Runs unconditionally (not version-gated) so a missing managed file
    at the current scaffold version still produces a repair action.
    Addresses the same-version inert-hook drift flagged in
    ``bridge/gtkb-hook-scanner-safe-writer-010.md`` Finding 1 and the
    same-version missing-skill drift flagged in
    ``bridge/gtkb-skill-decision-capture-009.md`` Finding 1.
    """
    actions: list[UpgradeAction] = []
    for mfile in (
        _filter_hooks_for_profile(profile) + _filter_rules_for_profile(profile) + _filter_skills_for_profile(profile)
    ):
        project_path = target / mfile
        if project_path.exists():
            continue
        template_rel = _map_managed_to_template(mfile)
        if template_rel is None:
            continue
        if _template_hash(template_rel) is None:
            continue
        actions.append(
            UpgradeAction(
                file=mfile,
                action="add",
                reason="Managed file missing — will copy from template",
            )
        )
    return actions


def _plan_managed_hooks(target: Path, profile: ProjectProfile) -> list[UpgradeAction]:
    """Plan ``add``/``skip`` actions for managed ``.claude/hooks/`` files.

    Behavior preserved from the original in-line planning loop:
    - ``local-only`` profile only carries ``assertion-check.py`` and
      ``spec-classifier.py``.
    - Missing files produce an ``add`` action.
    - Files that differ from the template produce a ``skip`` action with a
      "customized?" reason (requiring ``--force`` to overwrite).
    - Files that match the template are silently skipped.
    """
    actions: list[UpgradeAction] = []
    for mfile in _filter_hooks_for_profile(profile):
        project_path = target / mfile
        if not project_path.exists():
            continue  # Missing-file case handled by _plan_missing_managed_files

        template_rel = _map_managed_to_template(mfile)
        if template_rel is None:
            continue

        template_h = _template_hash(template_rel)
        if template_h is None:
            continue

        project_h = _file_hash(project_path)
        if project_h == template_h:
            continue  # Already current

        # User-customized file — require --force to overwrite
        actions.append(
            UpgradeAction(
                file=mfile,
                action="skip",
                reason="File differs from template (customized?) — use --force to overwrite",
            )
        )

    return actions


def _plan_managed_rules(target: Path, profile: ProjectProfile) -> list[UpgradeAction]:
    """Plan ``skip`` actions for managed ``.claude/rules/`` files that differ
    from the template. Missing-file case is handled by
    :func:`_plan_missing_managed_files`.
    """
    actions: list[UpgradeAction] = []
    for mfile in _filter_rules_for_profile(profile):
        project_path = target / mfile
        if not project_path.exists():
            continue  # Missing-file case handled by _plan_missing_managed_files

        template_rel = _map_managed_to_template(mfile)
        if template_rel is None:
            continue

        template_h = _template_hash(template_rel)
        if template_h is None:
            continue

        project_h = _file_hash(project_path)
        if project_h == template_h:
            continue

        actions.append(
            UpgradeAction(
                file=mfile,
                action="skip",
                reason="File differs from template (customized?) — use --force to overwrite",
            )
        )

    return actions


def _plan_managed_skills(target: Path, profile: ProjectProfile) -> list[UpgradeAction]:
    """Plan ``skip`` actions for managed ``.claude/skills/`` files that differ
    from the template. Missing-file case is handled by
    :func:`_plan_missing_managed_files`.

    Version-gated: only runs when ``scaffold_version != __version__``.
    Parallel in shape to :func:`_plan_managed_hooks` and
    :func:`_plan_managed_rules`.
    """
    actions: list[UpgradeAction] = []
    for mfile in _filter_skills_for_profile(profile):
        project_path = target / mfile
        if not project_path.exists():
            continue  # Missing-file case handled by _plan_missing_managed_files

        template_rel = _map_managed_to_template(mfile)
        if template_rel is None:
            continue

        template_h = _template_hash(template_rel)
        if template_h is None:
            continue

        project_h = _file_hash(project_path)
        if project_h == template_h:
            continue

        actions.append(
            UpgradeAction(
                file=mfile,
                action="skip",
                reason="File differs from template (customized?) — use --force to overwrite",
            )
        )

    return actions


def _plan_settings_registration(target: Path, profile: ProjectProfile) -> list[UpgradeAction]:
    """Plan PreToolUse registrations for managed hooks in ``settings.json``.

    Emits ``register-hook`` actions for hooks listed in
    :data:`_MANAGED_SETTINGS_PRETOOLUSE_HOOKS` that are NOT already
    registered in ``.claude/settings.json``.

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
    for hook_name, bridge_only in _MANAGED_SETTINGS_PRETOOLUSE_HOOKS:
        if bridge_only and not profile.includes_bridge:
            continue
        marker = f"python .claude/hooks/{hook_name}"
        if any(marker in cmd for cmd in registered_commands):
            continue
        actions.append(
            UpgradeAction(
                file=".claude/settings.json",
                action="register-hook",
                reason=f"Register {hook_name} as PreToolUse hook",
                payload=hook_name,
            )
        )
    return actions


def _plan_gitignore_patterns(target: Path, profile: ProjectProfile) -> list[UpgradeAction]:
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
    for pattern, comment, bridge_only in _MANAGED_GITIGNORE_PATTERNS:
        if bridge_only and not profile.includes_bridge:
            continue
        if pattern in existing_lines:
            continue
        actions.append(
            UpgradeAction(
                file=".gitignore",
                action="append-gitignore",
                reason=f"Append pattern: {pattern} ({comment})",
                payload=pattern,
            )
        )
    return actions


def plan_upgrade(target: Path) -> list[UpgradeAction]:
    """Plan the upgrade: managed-file updates + config drift repairs.

    Always runs settings and gitignore drift checks so that config drift is
    repaired even when the scaffold version is already current. Managed
    hook/rule file updates remain gated on ``scaffold_version != __version__``
    to avoid unnecessary re-copy of unchanged files.
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
    actions.extend(_plan_missing_managed_files(target, profile))
    actions.extend(_plan_settings_registration(target, profile))
    actions.extend(_plan_gitignore_patterns(target, profile))

    # Managed-file hash/customization checks are gated on version change —
    # at the current version, files present on disk are assumed to match
    # the template (or be intentional customizations). Missing files are
    # already handled above.
    if manifest.scaffold_version != __version__:
        actions.extend(_plan_managed_hooks(target, profile))
        actions.extend(_plan_managed_rules(target, profile))
        actions.extend(_plan_managed_skills(target, profile))

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
        template_rel = _map_managed_to_template(action.file)

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
