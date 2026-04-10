# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Project upgrade — ``gt project upgrade`` implementation."""

from __future__ import annotations

import hashlib
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from groundtruth_kb import __version__, get_templates_dir
from groundtruth_kb.project.manifest import read_manifest, write_manifest
from groundtruth_kb.project.profiles import get_profile


@dataclass
class UpgradeAction:
    """A single file action in the upgrade plan."""

    file: str
    action: Literal["update", "add", "skip"]
    reason: str


# Files managed by the scaffold (overwritten on upgrade unless customized)
_MANAGED_HOOKS = [
    ".claude/hooks/assertion-check.py",
    ".claude/hooks/spec-classifier.py",
    ".claude/hooks/destructive-gate.py",
    ".claude/hooks/credential-scan.py",
    ".claude/hooks/scheduler.py",
]
_MANAGED_RULES = [
    ".claude/rules/prime-builder.md",
    ".claude/rules/loyal-opposition.md",
    ".claude/rules/bridge-poller-canonical.md",
    ".claude/rules/prime-bridge-collaboration-protocol.md",
    ".claude/rules/report-depth.md",
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
    return None


def plan_upgrade(target: Path) -> list[UpgradeAction]:
    """Compare scaffold version to installed version, plan file updates."""
    manifest = read_manifest(target / "groundtruth.toml")
    if manifest is None:
        return [
            UpgradeAction(
                file="groundtruth.toml",
                action="skip",
                reason="No [project] manifest found — run `gt project init` first",
            )
        ]

    if manifest.scaffold_version == __version__:
        return []

    profile = get_profile(manifest.profile)
    actions: list[UpgradeAction] = []

    # Check managed hooks
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

    for mfile in managed:
        project_path = target / mfile
        template_rel = _map_managed_to_template(mfile)
        if template_rel is None:
            continue

        template_h = _template_hash(template_rel)
        if template_h is None:
            continue

        if not project_path.exists():
            actions.append(UpgradeAction(file=mfile, action="add", reason="New managed file"))
            continue

        project_h = _file_hash(project_path)
        if project_h == template_h:
            continue  # Already current

        # Check if user customized the file
        actions.append(
            UpgradeAction(
                file=mfile,
                action="skip",
                reason="File differs from template (customized?) — use --force to overwrite",
            )
        )

    # Check managed rules
    managed_rules = list(_MANAGED_RULES)
    if not profile.includes_bridge:
        managed_rules = [r for r in managed_rules if "prime-builder" in r]

    for mfile in managed_rules:
        project_path = target / mfile
        template_rel = _map_managed_to_template(mfile)
        if template_rel is None:
            continue

        template_h = _template_hash(template_rel)
        if template_h is None:
            continue

        if not project_path.exists():
            actions.append(UpgradeAction(file=mfile, action="add", reason="New managed file"))
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
