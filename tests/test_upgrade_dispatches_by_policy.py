# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Upgrade dispatches by ``ownership.upgrade_policy``.

Proposal §3.3 — upgrade correctly dispatches overwrite / preserve /
structured-merge / transient paths. Because all 40 current-HEAD registry rows
use ``overwrite`` or ``structured-merge``, the existing behavior is a
regression gate: dispatch must be bit-identical. Pure-policy routing for
``preserve`` / ``transient`` / ``adopter-opt-in`` is exercised against a
synthetic artifact list to avoid mutating the production registry.
"""

from __future__ import annotations

from pathlib import Path

from groundtruth_kb.project import upgrade as upgrade_mod
from groundtruth_kb.project.managed_registry import (
    FileArtifact,
    _parse_record,
    artifacts_for_upgrade,
)

# ---------------------------------------------------------------------------
# Regression: existing 40-row behavior must be unchanged
# ---------------------------------------------------------------------------


def test_all_existing_rows_use_non_preserving_policies() -> None:
    """Sanity: every registry row has overwrite or structured-merge policy.

    If this ever fails, a NEW row with preserve/transient/adopter-opt-in has
    been added to the registry (not via ownership-glob). Review whether the
    upgrade semantics for that row are intentional.
    """
    rows = artifacts_for_upgrade("dual-agent-webapp")  # broadest profile
    offenders = [
        a
        for a in rows
        if a.class_ != "ownership-glob"
        and hasattr(a, "ownership")
        and a.ownership is not None
        and a.ownership.upgrade_policy not in ("overwrite", "structured-merge")
    ]
    assert offenders == [], f"unexpected upgrade policies on registry rows: {[a.id for a in offenders]}"


def test_managed_file_artifacts_filters_out_preserve_policy(monkeypatch) -> None:
    """A synthetic hook with upgrade_policy='preserve' must be excluded from upgrade plan."""
    # Build a single fake record with preserve policy.
    fake_preserve_hook: FileArtifact = _parse_record(
        {
            "class": "hook",
            "id": "hook.test-preserve",
            "template_path": "hooks/x.py",
            "target_path": ".claude/hooks/x.py",
            "initial_profiles": ["local-only"],
            "managed_profiles": ["local-only"],
            "doctor_required_profiles": [],
            "ownership": "gt-kb-scaffolded",
            "upgrade_policy": "preserve",
        }
    )  # type: ignore[assignment]
    assert isinstance(fake_preserve_hook, FileArtifact)

    # Patch artifacts_for_upgrade to inject our synthetic row alongside the
    # real ones so the ownership-policy filter is exercised end-to-end.
    real = artifacts_for_upgrade

    def _fake(profile, class_=None):
        rows = real(profile, class_=class_)
        if class_ in (None, "hook"):
            rows = [*rows, fake_preserve_hook]
        return rows

    monkeypatch.setattr(upgrade_mod, "artifacts_for_upgrade", _fake)

    # The private helper that wraps artifacts_for_upgrade must drop the preserve row.
    result_ids = {a.id for a in upgrade_mod._managed_file_artifacts("local-only", "hook")}
    assert "hook.test-preserve" not in result_ids
    # But the normal overwrite-policy hooks are still there.
    assert "hook.assertion-check" in result_ids


def test_managed_file_artifacts_filters_out_transient_policy(monkeypatch) -> None:
    """A synthetic hook with upgrade_policy='transient' is also excluded."""
    fake_transient: FileArtifact = _parse_record(
        {
            "class": "hook",
            "id": "hook.test-transient",
            "template_path": "hooks/x.py",
            "target_path": ".claude/hooks/x.py",
            "initial_profiles": ["local-only"],
            "managed_profiles": ["local-only"],
            "doctor_required_profiles": [],
            "ownership": "gt-kb-managed",
            "upgrade_policy": "transient",
        }
    )  # type: ignore[assignment]

    real = artifacts_for_upgrade

    def _fake(profile, class_=None):
        rows = real(profile, class_=class_)
        if class_ in (None, "hook"):
            rows = [*rows, fake_transient]
        return rows

    monkeypatch.setattr(upgrade_mod, "artifacts_for_upgrade", _fake)
    result_ids = {a.id for a in upgrade_mod._managed_file_artifacts("local-only", "hook")}
    assert "hook.test-transient" not in result_ids


def test_managed_file_artifacts_filters_out_adopter_opt_in(monkeypatch) -> None:
    """adopter-opt-in rows are withheld from the default upgrade plan."""
    fake_opt_in: FileArtifact = _parse_record(
        {
            "class": "hook",
            "id": "hook.test-opt-in",
            "template_path": "hooks/x.py",
            "target_path": ".claude/hooks/x.py",
            "initial_profiles": ["local-only"],
            "managed_profiles": ["local-only"],
            "doctor_required_profiles": [],
            "ownership": "adopter-owned",
            "upgrade_policy": "adopter-opt-in",
            "adopter_divergence_policy": "warn",
        }
    )  # type: ignore[assignment]

    real = artifacts_for_upgrade

    def _fake(profile, class_=None):
        rows = real(profile, class_=class_)
        if class_ in (None, "hook"):
            rows = [*rows, fake_opt_in]
        return rows

    monkeypatch.setattr(upgrade_mod, "artifacts_for_upgrade", _fake)
    result_ids = {a.id for a in upgrade_mod._managed_file_artifacts("local-only", "hook")}
    assert "hook.test-opt-in" not in result_ids


def test_managed_file_artifacts_includes_overwrite_policy() -> None:
    """overwrite-policy hooks are included (regression gate)."""
    result_ids = {a.id for a in upgrade_mod._managed_file_artifacts("local-only", "hook")}
    assert "hook.assertion-check" in result_ids
    assert "hook.spec-classifier" in result_ids


def test_plan_upgrade_current_registry_bit_identical_for_same_version(tmp_path: Path) -> None:
    """``plan_upgrade`` against a current-version scaffold emits no file actions.

    This is a regression gate: integration of OwnershipResolver must not
    change the existing 'same-version means no file-drift actions' contract.
    """
    from groundtruth_kb import __version__

    # Write a minimal manifest at current scaffold_version.
    (tmp_path / "groundtruth.toml").write_text(
        f"""[groundtruth]
db_path = "groundtruth.db"

[project]
project_name = "Test"
owner = "Test"
profile = "local-only"
copyright_notice = ""
cloud_provider = "none"
scaffold_version = "{__version__}"
created_at = "2026-01-01T00:00:00Z"
""",
        encoding="utf-8",
    )

    # Copy templates so missing-file planner finds them.
    from groundtruth_kb import get_templates_dir

    templates = get_templates_dir()
    for hook in ["assertion-check.py", "spec-classifier.py"]:
        src = templates / "hooks" / hook
        dst = tmp_path / ".claude" / "hooks" / hook
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())

    rule_src = templates / "rules" / "prime-builder.md"
    rule_dst = tmp_path / ".claude" / "rules" / "prime-builder.md"
    rule_dst.parent.mkdir(parents=True, exist_ok=True)
    rule_dst.write_bytes(rule_src.read_bytes())

    actions = upgrade_mod.plan_upgrade(tmp_path)
    # No managed-file drift actions (local-only has no settings.json or gitignore
    # managed for upgrade either).
    file_actions = [a for a in actions if a.action in ("add", "skip", "update")]
    assert file_actions == [], f"unexpected file actions: {file_actions}"
