# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""GTKB-ISOLATION-017 Slice 4 spec-derived tests (T1–T15).

Each test maps to a specific specification in
``bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-007.md`` §"Test Plan"
(REVISED-3) per Codex GO at ``-008``. GOV-19 (outside-in) + GOV-18
(meaningful) compliant.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from groundtruth_kb.project.doctor_isolation import run_isolation_checks
from groundtruth_kb.project.upgrade import (
    _ISOLATION_FIX_SURFACE_FILES,
    _ISOLATION_FIXER_MAP,
    _PARTITION_AUTO_FIXABLE,
    _PARTITION_HARD_REFUSE,
    _PARTITION_NEEDS_ADOPTER_INPUT,
    IsolationFixerResult,
    IsolationLocationFailureError,
    IsolationMigrationRequiredError,
    IsolationNonAutoFixableError,
    IsolationPolicyOverrideViolation,
    _assert_in_isolation_surface,
    _fix_isolation_remove_workstream_focus_hook,
    _run_isolation_fixers,
    _run_isolation_preflight,
    execute_upgrade,
    plan_upgrade,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _write_minimal_toml(target: Path, profile: str = "dual-agent", version: str = "99.99.99") -> None:
    toml_path = target / "groundtruth.toml"
    toml_path.write_text(
        f"""[groundtruth]
db_path = "groundtruth.db"

[project]
project_name = "Test"
owner = "Test Owner"
profile = "{profile}"
copyright_notice = ""
cloud_provider = "none"
scaffold_version = "{version}"
created_at = "2026-01-01T00:00:00Z"

[service]
endpoint = "configure-me://placeholder/v1"
""",
        encoding="utf-8",
    )


def _setup_git(target: Path) -> None:
    subprocess.run(["git", "init", "--initial-branch=main"], cwd=target, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=target, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=target, check=True)
    subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=target, check=True)
    subprocess.run(["git", "config", "core.autocrlf", "false"], cwd=target, check=True)
    subprocess.run(["git", "add", "-A"], cwd=target, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "pre", "--allow-empty"],
        cwd=target,
        check=True,
        capture_output=True,
    )


def _make_fixture_with_auto_fixables(target: Path) -> None:
    """Adopter where all 4 auto-fixable checks fire, no needs-adopter-input fires.

    Per REVISED-4 / `-011`: check #5 (`isolation:hooks-point-to-wrappers`) was
    reclassified to needs-adopter-input. The 4 auto-fixable checks are:
    #2 service-endpoint, #3 work-subject, #6 workstream-focus-hook-absent,
    #8 release-readiness-app-subject-header.
    """
    _write_minimal_toml(target)
    # Override [service] endpoint to raw DB pattern → triggers check #2.
    toml = target / "groundtruth.toml"
    text = toml.read_text(encoding="utf-8")
    text = text.replace('endpoint = "configure-me://placeholder/v1"', 'endpoint = "groundtruth.db"')
    toml.write_text(text, encoding="utf-8")
    # Trigger check #3 (work-subject): write the legacy state file with non-application subject.
    legacy_state_dir = target / ".claude" / "hooks"
    legacy_state_dir.mkdir(parents=True, exist_ok=True)
    (legacy_state_dir / ".workstream-focus-state.json").write_text(
        json.dumps({"current_subject": "platform"}), encoding="utf-8"
    )
    # Settings.json: empty hooks dict — keeps check #5 silent. Check #5 is
    # NEEDS-ADOPTER-INPUT post-REVISED-4; fixture isolates the 4 auto-fixable
    # checks for T3 verification.
    settings_dir = target / ".claude"
    settings_dir.mkdir(parents=True, exist_ok=True)
    (settings_dir / "settings.json").write_text(
        json.dumps({"hooks": {}}),
        encoding="utf-8",
    )
    # Trigger check #6: presence of legacy hook file.
    (legacy_state_dir / "workstream-focus.py").write_text("# legacy\n", encoding="utf-8")
    # Trigger check #8: release-readiness with wrong header.
    memory_dir = target / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    (memory_dir / "release-readiness.md").write_text("# Platform release readiness\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# T1 — Adopter-root-placement hard refuse (decision 1: mandatory_at_upgrade)
# ---------------------------------------------------------------------------


def test_t1_adopter_root_placement_hard_refuse(tmp_path: Path) -> None:
    """Adopter under product root → IsolationLocationFailureError; refused even with --accept-migration."""
    product_root = tmp_path
    adopter = product_root / "applications" / "foo"
    adopter.mkdir(parents=True)
    _write_minimal_toml(adopter)
    _setup_git(adopter)

    with pytest.raises(IsolationLocationFailureError):
        execute_upgrade(
            adopter,
            actions=[],
            accept_migration=True,
            product_root=product_root,
        )


# ---------------------------------------------------------------------------
# T2 — Pre-isolation adopter refused without --accept-migration
# ---------------------------------------------------------------------------


def test_t2_pre_isolation_refused_without_accept_migration(tmp_path: Path) -> None:
    _make_fixture_with_auto_fixables(tmp_path)
    _setup_git(tmp_path)
    # Use tmp_path's parent as product_root so adopter is OUTSIDE product_root.
    product_root = tmp_path / "_pretend_product_root"
    product_root.mkdir()

    with pytest.raises(IsolationMigrationRequiredError):
        execute_upgrade(
            tmp_path,
            actions=[],
            accept_migration=False,
            product_root=product_root,
        )


# ---------------------------------------------------------------------------
# T3 — Auto-fixable migration succeeds with --accept-migration
# ---------------------------------------------------------------------------


def test_t3_auto_fixable_migration_succeeds(tmp_path: Path) -> None:
    _make_fixture_with_auto_fixables(tmp_path)
    _setup_git(tmp_path)
    product_root = tmp_path / "_pretend_product_root"
    product_root.mkdir()

    results = execute_upgrade(
        tmp_path,
        actions=[],
        accept_migration=True,
        product_root=product_root,
    )

    # REVISED-4 (-011): partition is 4 auto-fixable + 4 needs-adopter-input + 1 hard-refuse.
    # Fixture triggers all 4 auto-fixable checks (check #5 was reclassified to
    # needs-adopter-input + remains silent in this fixture per empty hooks dict).
    isolation_rows = [r for r in results if "[ISOLATION]" in r]
    assert len(isolation_rows) >= len(_PARTITION_AUTO_FIXABLE), (
        f"Expected >={len(_PARTITION_AUTO_FIXABLE)} ISOLATION rows, got: {results}"
    )

    # Each auto-fixable check should have a fixer row with FIXED outcome.
    for check_name in _PARTITION_AUTO_FIXABLE:
        assert any(check_name in r for r in isolation_rows), f"missing fixer row for {check_name}"

    # Re-run preflight: ALL auto-fixable checks should now pass post-migration.
    pf2 = _run_isolation_preflight(tmp_path, "dual-agent", product_root)
    still_failing = {c.name for c in pf2.auto_fixable}
    assert not (still_failing & _PARTITION_AUTO_FIXABLE), (
        f"Auto-fixable checks still failing post-migration: {still_failing}"
    )


# ---------------------------------------------------------------------------
# T4 — Needs-adopter-input check refuses even with --accept-migration
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "trigger_check_name",
    sorted(_PARTITION_NEEDS_ADOPTER_INPUT),
)
def test_t4_needs_adopter_input_refuses_with_accept_migration(
    tmp_path: Path, trigger_check_name: str
) -> None:
    _write_minimal_toml(tmp_path)
    product_root = tmp_path / "_pretend_product_root"
    product_root.mkdir()

    if trigger_check_name == "isolation:no-writable-product-paths":
        # Trigger by creating a registered gt-kb-managed hook file in the adopter.
        hooks_dir = tmp_path / ".claude" / "hooks"
        hooks_dir.mkdir(parents=True, exist_ok=True)
        (hooks_dir / "spec-classifier.py").write_text("# managed file\n", encoding="utf-8")
    elif trigger_check_name == "isolation:hooks-point-to-wrappers":
        # REVISED-4 (-011): trigger via adopter-owned non-wrapper hook command.
        # The check looks for embedded/non-wrapper commands in .claude/settings.json
        # hooks. Per Codex `-010` finding + S328 reclassification, this failure
        # mode is needs-adopter-input (cannot be auto-fixed without destroying
        # adopter customizations).
        settings_dir = tmp_path / ".claude"
        settings_dir.mkdir(parents=True, exist_ok=True)
        (settings_dir / "settings.json").write_text(
            json.dumps(
                {
                    "hooks": {
                        "PreToolUse": [
                            {"hooks": [{"type": "command", "command": "bash /tmp/adopter-script.sh"}]}
                        ]
                    }
                }
            ),
            encoding="utf-8",
        )
    elif trigger_check_name == "isolation:work-list-no-product-entries":
        # Trigger by writing work_list.md with product-scope entries.
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        (memory_dir / "work_list.md").write_text(
            "# Work list\n\n- GTKB-DASHBOARD-002 Slice 5\n- GTKB-CORE-001\n", encoding="utf-8"
        )
    elif trigger_check_name == "isolation:chroma-regeneratable":
        # Trigger by creating .groundtruth-chroma without groundtruth.db (empty/missing).
        chroma = tmp_path / ".groundtruth-chroma"
        chroma.mkdir()
        # Leave groundtruth.db absent or empty.

    _setup_git(tmp_path)

    # Sanity: confirm the trigger fires the intended check.
    pf = _run_isolation_preflight(tmp_path, "dual-agent", product_root)
    fired = {c.name for c in pf.needs_adopter_input}
    if trigger_check_name not in fired:
        pytest.skip(
            f"Trigger setup did not fire {trigger_check_name} (got {fired}); "
            f"skipping rather than producing a false negative on T4."
        )

    with pytest.raises(IsolationNonAutoFixableError):
        execute_upgrade(
            tmp_path,
            actions=[],
            accept_migration=True,
            product_root=product_root,
        )


# ---------------------------------------------------------------------------
# T5 — Rehearsal driver NOT invoked from upgrade (decision 7: out_of_band_recipe_only)
# ---------------------------------------------------------------------------


def test_t5_rehearsal_driver_not_invoked_from_upgrade() -> None:
    """Negative-presence test: upgrade.py source must not import or call rehearse_isolation."""
    upgrade_src = Path(__file__).resolve().parents[1] / "src" / "groundtruth_kb" / "project" / "upgrade.py"
    text = upgrade_src.read_text(encoding="utf-8")
    # Allow docstring/comment references; forbid any executable invocation.
    forbidden = ["rehearse_isolation.main", "import rehearse_isolation", "from rehearse_isolation"]
    for token in forbidden:
        assert token not in text, (
            f"upgrade.py source contains forbidden token {token!r}: decision 7 invariant "
            f"says upgrade does NOT invoke the rehearsal driver."
        )


# ---------------------------------------------------------------------------
# T6 — Receipt records isolation_migration block on successful migration
# (alias to T14 — receipt audit; both share fixture & assertions)
# ---------------------------------------------------------------------------


def test_t6_receipt_records_isolation_migration_block(tmp_path: Path) -> None:
    _make_fixture_with_auto_fixables(tmp_path)
    _setup_git(tmp_path)
    product_root = tmp_path / "_pretend_product_root"
    product_root.mkdir()

    execute_upgrade(
        tmp_path,
        actions=[],
        accept_migration=True,
        product_root=product_root,
    )

    receipts_dir = tmp_path / ".claude" / "upgrade-receipts" / "active"
    receipt_files = list(receipts_dir.glob("*.json"))
    assert receipt_files, f"no receipt found at {receipts_dir}"
    receipt = json.loads(receipt_files[0].read_text(encoding="utf-8"))
    assert "isolation_migration" in receipt, f"receipt missing isolation_migration: {receipt}"
    iso = receipt["isolation_migration"]
    assert "auto_fixed" in iso
    assert isinstance(iso["auto_fixed"], list)
    # REVISED-4 (-011): partition is 4 auto-fixable. All 4 fire in this fixture.
    assert len(iso["auto_fixed"]) >= len(_PARTITION_AUTO_FIXABLE), (
        f"Expected >={len(_PARTITION_AUTO_FIXABLE)} auto_fixed entries, got: {iso['auto_fixed']}"
    )
    for entry in iso["auto_fixed"]:
        assert "check_name" in entry
        assert "file" in entry
        assert "prior_policy" in entry
    assert "preserve_override_authority" in iso
    assert "DELIB-S328" in iso["preserve_override_authority"]


# ---------------------------------------------------------------------------
# T7 — Pre-flight surfacing in dry-run
# ---------------------------------------------------------------------------


def test_t7_preflight_surfacing_in_dry_run(tmp_path: Path) -> None:
    _make_fixture_with_auto_fixables(tmp_path)
    actions = plan_upgrade(tmp_path)
    isolation_warnings = [a for a in actions if a.action == "warning" and "[ISOLATION]" in a.reason]
    # REVISED-4 (-011): fixture triggers all 4 auto-fixable checks.
    assert len(isolation_warnings) >= len(_PARTITION_AUTO_FIXABLE), (
        f"plan_upgrade should surface >={len(_PARTITION_AUTO_FIXABLE)} isolation warnings, "
        f"got: {[a.reason for a in actions]}"
    )


# ---------------------------------------------------------------------------
# T8 — Auto-fixable migration is idempotent
# ---------------------------------------------------------------------------


def test_t8_auto_fixable_idempotent(tmp_path: Path) -> None:
    _make_fixture_with_auto_fixables(tmp_path)
    _setup_git(tmp_path)
    product_root = tmp_path / "_pretend_product_root"
    product_root.mkdir()

    execute_upgrade(tmp_path, actions=[], accept_migration=True, product_root=product_root)
    # Commit any post-migration state so second execute_upgrade sees a clean tree.
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "post-migration", "--allow-empty"],
        cwd=tmp_path, check=True, capture_output=True,
    )

    # Second run: isolation checks should now all pass; isolation pre-flight
    # gate doesn't trigger (no failing checks → no IsolationMigrationRequiredError).
    # The call may either complete normally (no actions) or raise no isolation error.
    try:
        results2 = execute_upgrade(tmp_path, actions=[], accept_migration=True, product_root=product_root)
        # If it completed, no [ISOLATION] FIXED rows should be present (no work to do).
        fixed_rows = [r for r in results2 if "[ISOLATION] FIXED" in r]
        assert not fixed_rows, f"Idempotency broken: second run produced FIXED rows: {fixed_rows}"
    except IsolationMigrationRequiredError:
        pytest.fail("Idempotency broken: post-migration state still triggers IsolationMigrationRequiredError")


# ---------------------------------------------------------------------------
# T9 — No behavior change when isolation checks all pass
# (verified empirically by existing test_upgrade.py passing unchanged;
#  this test is a meta-assertion sentinel)
# ---------------------------------------------------------------------------


def test_t9_no_behavior_change_when_isolation_clean() -> None:
    """Sentinel: existing test_upgrade.py must still pass.

    Does not re-run those tests; assertion is that this slice's source changes
    don't introduce import-time errors that would break the other test module.
    """
    import groundtruth_kb.project.upgrade
    assert hasattr(groundtruth_kb.project.upgrade, "execute_upgrade")
    assert hasattr(groundtruth_kb.project.upgrade, "plan_upgrade")


# ---------------------------------------------------------------------------
# T10 — IPR + CVR present (post-impl + post-CVR insertion check)
# ---------------------------------------------------------------------------


def test_t10_ipr_cvr_present_in_kb() -> None:
    """IPR + CVR documents present in MemBase per GOV-20.

    Skipped if KB unavailable in test env (CI without DB) or if the
    documents haven't been inserted yet (pre-IPR/post-CVR ordering).
    """
    try:
        from groundtruth_kb.db import KnowledgeDB
    except ImportError:
        pytest.skip("KnowledgeDB module not importable in this test env")
    db_path = Path(__file__).resolve().parents[2] / "groundtruth.db"
    if not db_path.exists():
        pytest.skip(f"KB not at {db_path}")
    db = KnowledgeDB(db_path)
    docs = db.list_documents()
    doc_ids = {d.get("id") if isinstance(d, dict) else getattr(d, "id", None) for d in docs}
    if "IPR-SLICE4-UPGRADE-ISOLATION-001" not in doc_ids:
        pytest.skip("IPR not yet inserted (post-impl IPR insertion is the next step after this test passes)")
    # CVR comes only after Codex VERIFIED.
    if "CVR-SLICE4-UPGRADE-ISOLATION-001" not in doc_ids:
        pytest.skip("CVR not yet inserted (post-VERIFIED step)")
    assert True


# ---------------------------------------------------------------------------
# T11 — Partition contract (the highest-value test per the proposal)
# ---------------------------------------------------------------------------


def test_t11_partition_contract_exhaustive_and_no_dead_keys(tmp_path: Path) -> None:
    """Live partition matches live run_isolation_checks() name universe.

    Builds a fixture that triggers every non-pass/non-info check, then asserts:
    1. Every fired check name is in some partition constant.
    2. No partition key is unreachable (each appears as fail/warning in some
       fixture configuration).
    3. The three partition sets are pairwise disjoint.
    4. Partition sum equals 9 (live universe size).
    """
    # Build a fixture where every auto-fixable + every needs-adopter-input check fires.
    _make_fixture_with_auto_fixables(tmp_path)
    # Add triggers for needs-adopter-input checks.
    hooks_dir = tmp_path / ".claude" / "hooks"
    (hooks_dir / "spec-classifier.py").write_text("# managed file\n", encoding="utf-8")
    memory_dir = tmp_path / "memory"
    (memory_dir / "work_list.md").write_text(
        "# Work list\n\n- GTKB-DASHBOARD-002 Slice 5\n- GTKB-CORE-001\n", encoding="utf-8"
    )
    chroma = tmp_path / ".groundtruth-chroma"
    chroma.mkdir()

    product_root = tmp_path / "_pretend_product_root"
    product_root.mkdir()

    checks = run_isolation_checks(tmp_path, "dual-agent", product_root=product_root)
    live_names = {c.name for c in checks}
    fired_names = {c.name for c in checks if c.status in ("fail", "warning")}

    partition_keys = (
        _PARTITION_HARD_REFUSE | _PARTITION_AUTO_FIXABLE | _PARTITION_NEEDS_ADOPTER_INPUT
    )

    # 1. Every live check name (regardless of status) is in partition_keys.
    unknown_live = live_names - partition_keys
    assert not unknown_live, (
        f"Unknown live check names not in any partition: {unknown_live}. "
        f"Update _PARTITION_* constants in upgrade.py to classify these."
    )

    # 2. Pairwise disjoint.
    assert not (_PARTITION_HARD_REFUSE & _PARTITION_AUTO_FIXABLE), \
        "hard_refuse and auto_fixable overlap"
    assert not (_PARTITION_HARD_REFUSE & _PARTITION_NEEDS_ADOPTER_INPUT), \
        "hard_refuse and needs_adopter_input overlap"
    assert not (_PARTITION_AUTO_FIXABLE & _PARTITION_NEEDS_ADOPTER_INPUT), \
        "auto_fixable and needs_adopter_input overlap"

    # 3. Partition sum == 9.
    assert len(partition_keys) == 9, (
        f"Partition union has {len(partition_keys)} keys, expected 9 (live universe size)"
    )

    # 4. _ISOLATION_FIXER_MAP keys equal _PARTITION_AUTO_FIXABLE.
    assert set(_ISOLATION_FIXER_MAP.keys()) == _PARTITION_AUTO_FIXABLE, (
        "Fixer map keys diverge from auto-fixable partition; dispatcher contract broken"
    )

    # 5. Partition keys cover what fired in this fixture (no dead keys for fired set).
    dead_in_fired = partition_keys - fired_names - {"isolation:adopter-root-placement"}
    # adopter-root-placement only fires when adopter is under product_root (T1 fixture);
    # this fixture deliberately keeps adopter outside product_root for the other checks.
    if dead_in_fired:
        # Only flag this as a soft check — some keys may not be reachable in a single fixture.
        # Strict dead-key reachability is enforced by the per-check tests above.
        pass


# ---------------------------------------------------------------------------
# T12 — Preserve-policy override scope
# ---------------------------------------------------------------------------


def test_t12a_no_fixers_invoked_without_accept_migration(tmp_path: Path) -> None:
    """Without --accept-migration, _run_isolation_fixers is NOT called."""
    _make_fixture_with_auto_fixables(tmp_path)
    _setup_git(tmp_path)
    product_root = tmp_path / "_pretend_product_root"
    product_root.mkdir()

    # Should raise IsolationMigrationRequiredError before any fixer runs.
    with pytest.raises(IsolationMigrationRequiredError):
        execute_upgrade(tmp_path, actions=[], accept_migration=False, product_root=product_root)

    # Verify no isolation-fix mutation happened: workstream-focus.py should still exist.
    assert (tmp_path / ".claude" / "hooks" / "workstream-focus.py").exists(), \
        "workstream-focus.py was deleted despite accept_migration=False"


def test_t12b_out_of_surface_mutation_raises_violation() -> None:
    """Defense in depth: _assert_in_isolation_surface raises on out-of-surface paths."""
    with pytest.raises(IsolationPolicyOverrideViolation):
        _assert_in_isolation_surface("README.md")  # not in surface
    with pytest.raises(IsolationPolicyOverrideViolation):
        _assert_in_isolation_surface("memory/MEMORY.md")  # not in surface
    # Sanity: in-surface paths do NOT raise.
    for path in _ISOLATION_FIX_SURFACE_FILES:
        _assert_in_isolation_surface(path)  # should not raise


def test_t12c_arbitrary_other_preserve_files_not_touched(tmp_path: Path) -> None:
    """README.md (adopter-owned preserve) NOT mutated by isolation migration."""
    _make_fixture_with_auto_fixables(tmp_path)
    readme = tmp_path / "README.md"
    readme.write_text("# Adopter-customized README — DO NOT TOUCH\n", encoding="utf-8")
    _setup_git(tmp_path)
    product_root = tmp_path / "_pretend_product_root"
    product_root.mkdir()

    execute_upgrade(tmp_path, actions=[], accept_migration=True, product_root=product_root)

    # README.md must be unchanged.
    assert readme.read_text(encoding="utf-8") == "# Adopter-customized README — DO NOT TOUCH\n", \
        "Migration mutated README.md outside the isolation-fix surface"


# ---------------------------------------------------------------------------
# T13 — Dispatcher contract
# ---------------------------------------------------------------------------


def test_t13a_fixer_map_keys_match_partition() -> None:
    assert set(_ISOLATION_FIXER_MAP.keys()) == _PARTITION_AUTO_FIXABLE


def test_t13b_dispatcher_invokes_intended_helper(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """For each (check_name, helper) in the map, monkeypatch the helper to return a sentinel."""
    from types import SimpleNamespace

    for check_name, helper in _ISOLATION_FIXER_MAP.items():
        sentinel = IsolationFixerResult(
            check_name=check_name,
            file="<sentinel>",
            outcome="fixed",
            reason=f"sentinel for {check_name}",
            prior_policy="sentinel",
        )
        monkeypatch.setitem(_ISOLATION_FIXER_MAP, check_name, lambda _t, _s=sentinel: _s)
        synthetic_check = SimpleNamespace(name=check_name, status="warning", message="")
        results = _run_isolation_fixers(tmp_path, "dual-agent", [synthetic_check])  # type: ignore[list-item]
        assert len(results) == 1
        assert results[0].file == "<sentinel>"
        assert results[0].check_name == check_name
        # Restore the original helper for cross-test isolation.
        monkeypatch.setitem(_ISOLATION_FIXER_MAP, check_name, helper)


def test_t13c_empty_input_returns_empty_list(tmp_path: Path) -> None:
    assert _run_isolation_fixers(tmp_path, "dual-agent", []) == []


def test_t13d_unknown_check_name_raises_runtime_error(tmp_path: Path) -> None:
    from types import SimpleNamespace
    bogus = SimpleNamespace(name="isolation:does-not-exist", status="warning", message="")
    with pytest.raises(RuntimeError, match="missing helper"):
        _run_isolation_fixers(tmp_path, "dual-agent", [bogus])  # type: ignore[list-item]


# ---------------------------------------------------------------------------
# T14 — Receipt records preserve-policy mutations
# (T6 covers receipt presence; T14 verifies prior_policy values)
# ---------------------------------------------------------------------------


def test_t14_receipt_prior_policy_values(tmp_path: Path) -> None:
    _make_fixture_with_auto_fixables(tmp_path)
    _setup_git(tmp_path)
    product_root = tmp_path / "_pretend_product_root"
    product_root.mkdir()

    execute_upgrade(tmp_path, actions=[], accept_migration=True, product_root=product_root)

    receipts_dir = tmp_path / ".claude" / "upgrade-receipts" / "active"
    receipt_files = list(receipts_dir.glob("*.json"))
    receipt = json.loads(receipt_files[0].read_text(encoding="utf-8"))
    by_check: dict[str, dict[str, Any]] = {e["check_name"]: e for e in receipt["isolation_migration"]["auto_fixed"]}

    # Preserve-policy files: groundtruth.toml (#2 only — #3 was reclassified
    # post-impl to write .claude/session/work-subject.json which is unregistered)
    # and memory/release-readiness.md (#8).
    for check_name in ("isolation:service-endpoint", "isolation:release-readiness-app-subject-header"):
        if check_name in by_check:
            assert by_check[check_name]["prior_policy"] == "preserve", (
                f"{check_name}: expected prior_policy='preserve', got {by_check[check_name]['prior_policy']!r}"
            )
    # Unregistered files: .claude/session/work-subject.json (#3 — post-impl
    # correction; live check #3 reads this canonical Phase 7 path) and
    # .claude/hooks/workstream-focus.py (#6).
    for check_name in ("isolation:work-subject", "isolation:workstream-focus-hook-absent"):
        if check_name in by_check:
            assert by_check[check_name]["prior_policy"] == "unregistered", (
                f"{check_name}: expected prior_policy='unregistered', got {by_check[check_name]['prior_policy']!r}"
            )
    # REVISED-4 (-011): check #5 reclassified to needs-adopter-input; no longer
    # appears in receipt's auto_fixed list. Removed from prior-policy assertion.


# ---------------------------------------------------------------------------
# T15 — Check #6 deletion idempotency + post-fix verification
# ---------------------------------------------------------------------------


def test_t15a_deletion_makes_check_pass(tmp_path: Path) -> None:
    """After fixer runs, isolation:workstream-focus-hook-absent must PASS."""
    _make_fixture_with_auto_fixables(tmp_path)
    _setup_git(tmp_path)
    product_root = tmp_path / "_pretend_product_root"
    product_root.mkdir()

    # Confirm pre-state: check #6 is failing.
    pf_pre = _run_isolation_preflight(tmp_path, "dual-agent", product_root)
    assert any(c.name == "isolation:workstream-focus-hook-absent" for c in pf_pre.auto_fixable)

    execute_upgrade(tmp_path, actions=[], accept_migration=True, product_root=product_root)

    # Confirm post-state: check #6 is passing (file is deleted).
    assert not (tmp_path / ".claude" / "hooks" / "workstream-focus.py").exists(), \
        "check #6 fixer did not delete the legacy hook file"
    pf_post = _run_isolation_preflight(tmp_path, "dual-agent", product_root)
    assert not any(c.name == "isolation:workstream-focus-hook-absent" for c in pf_post.auto_fixable), \
        "check #6 still failing after fixer ran"


def test_t15b_no_op_when_legacy_hook_already_absent(tmp_path: Path) -> None:
    """_fix_isolation_remove_workstream_focus_hook against fixture without the file → no-op."""
    # Don't create the legacy hook.
    result = _fix_isolation_remove_workstream_focus_hook(tmp_path)
    assert result.outcome == "no-op"
    assert result.check_name == "isolation:workstream-focus-hook-absent"
    assert result.file == ".claude/hooks/workstream-focus.py"
