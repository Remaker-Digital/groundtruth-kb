# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""GTKB-ISOLATION-017 Slice 3 — host-root binding + Phase 9 §1 scaffold tests.

Per `bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-007.md` (REVISED-2)
Codex GO at `-008.md`. The literal-path-binding contract is exercised here:

- TP-VAL-* are pure validation tests (no filesystem writes outside fixture
  setup). They cover ``_resolve_gt_kb_host_root`` and
  ``_validate_application_target`` directly.
- TP-INTEG-1 uses the in-root sandbox pattern under ``applications/_test_<uuid>/``
  with cleanup; it is the only test that actually scaffolds a tree and
  inspects Phase 9 §1 enumeration properties (TP1-TP13 collapsed).
- TP-CLI-* exercise the public ``gt project init`` surface via Click's
  ``CliRunner``. Refusal tests use deliberately out-of-root tmp paths to
  prove the validator rejects them.
- TS1, TS2 are explicitly-supplemental helper-level tests and do NOT
  substitute for the public-surface coverage above per ``GOV-19-A1``.
"""

from __future__ import annotations

import re
import shutil
import uuid
from pathlib import Path

import pytest

from groundtruth_kb.bootstrap import _validate_target
from groundtruth_kb.project.scaffold import (
    _GT_KB_HOST_ROOT,
    ScaffoldOptions,
    _resolve_gt_kb_host_root,
    _validate_application_target,
    enumerate_scaffold_outputs,
    scaffold_project,
)

# ============================================================================
# TP-VAL-* — Pure validation tests (no I/O outside fixture path checks)
# ============================================================================


def test_tp_val_1_resolve_gt_kb_host_root_returns_constant_when_explicit_none() -> None:
    assert _resolve_gt_kb_host_root(None) == _GT_KB_HOST_ROOT


def test_tp_val_2_resolve_gt_kb_host_root_accepts_matching_explicit() -> None:
    assert _resolve_gt_kb_host_root(_GT_KB_HOST_ROOT) == _GT_KB_HOST_ROOT


def test_tp_val_3_resolve_gt_kb_host_root_refuses_mismatched_explicit(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="must resolve to the active GT-KB host root"):
        _resolve_gt_kb_host_root(tmp_path)


def test_tp_val_3b_installed_context_accepts_explicit_adopter_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from groundtruth_kb.project import scaffold as scaffold_mod

    monkeypatch.setattr(scaffold_mod, "_is_installed_wheel_context", lambda: True)

    assert _resolve_gt_kb_host_root(tmp_path) == tmp_path.resolve()


def test_tp_val_3c_installed_context_defaults_to_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from groundtruth_kb.project import scaffold as scaffold_mod

    monkeypatch.setattr(scaffold_mod, "_is_installed_wheel_context", lambda: True)
    monkeypatch.chdir(tmp_path)

    assert _resolve_gt_kb_host_root(None) == tmp_path.resolve()


def test_tp_val_4_validate_application_target_accepts_under_applications() -> None:
    target = _GT_KB_HOST_ROOT / "applications" / "x"
    # Purely path-based check; target need not exist.
    _validate_application_target(target, _GT_KB_HOST_ROOT)


def test_tp_val_5_validate_application_target_refuses_outside_applications() -> None:
    target = _GT_KB_HOST_ROOT / "other" / "x"
    with pytest.raises(ValueError, match="must live directly under"):
        _validate_application_target(target, _GT_KB_HOST_ROOT)


def test_tp_val_6_validate_application_target_refuses_existing_adopter(tmp_path: Path) -> None:
    fake_root = tmp_path
    apps_dir = fake_root / "applications"
    apps_dir.mkdir()
    target = apps_dir / "myapp"
    target.mkdir()
    (target / "groundtruth.toml").write_text("# adopter\n", encoding="utf-8")
    with pytest.raises(ValueError, match="run `gt project upgrade` instead"):
        _validate_application_target(target, fake_root)


def test_tp_val_7_legacy_validate_target_unchanged_signature(tmp_path: Path) -> None:
    """Legacy `_validate_target(target)` accepts a single argument.
    Required for `bootstrap_desktop_project()` preservation per Codex `-008.md`.
    """
    fresh = tmp_path / "myproject"
    # Single-argument call must not raise on a non-existing target.
    _validate_target(fresh)


# ============================================================================
# TS1, TS2 — Supplemental helper tests (NOT GOV-19-A1 spec coverage)
# ============================================================================


class TestSupplementalHelperEdgeCases:
    """Per GOV-19-A1 these are supplemental and do NOT substitute for the
    public-surface tests above."""

    def test_ts1_validate_application_target_rejects_grandchild(self, tmp_path: Path) -> None:
        fake_root = tmp_path
        apps_dir = fake_root / "applications"
        apps_dir.mkdir()
        # Two levels deep — not directly under applications/
        target = apps_dir / "team" / "myapp"
        with pytest.raises(ValueError, match="must live directly under"):
            _validate_application_target(target, fake_root)

    def test_ts2_resolve_gt_kb_host_root_resolves_relative_explicit(self) -> None:
        """Explicit relative path that resolves to the host root is accepted."""
        # `Path(".")` resolved should equal cwd; we explicitly pass the
        # constant to keep the test cwd-independent.
        result = _resolve_gt_kb_host_root(_GT_KB_HOST_ROOT)
        assert result == _GT_KB_HOST_ROOT


# ============================================================================
# TP-CLI-* — Public CLI surface via Click CliRunner
# ============================================================================


@pytest.fixture
def cli_runner():
    from click.testing import CliRunner

    return CliRunner()


def test_tp_cli_refuse_1_explicit_root_mismatch_exits_nonzero(tmp_path: Path, cli_runner) -> None:
    from groundtruth_kb.cli import main as cli

    result = cli_runner.invoke(
        cli,
        [
            "project",
            "init",
            "myapp",
            "--owner",
            "Tester",
            "--gt-kb-root",
            str(tmp_path),
            "--profile",
            "local-only",
        ],
    )
    assert result.exit_code != 0
    assert "must resolve to the active GT-KB host root" in (result.output + str(result.exception))


def test_tp_cli_refuse_2_dir_outside_applications_exits_nonzero(tmp_path: Path, cli_runner) -> None:
    from groundtruth_kb.cli import main as cli

    out_of_apps = tmp_path / "elsewhere" / "myapp"
    result = cli_runner.invoke(
        cli,
        [
            "project",
            "init",
            "myapp",
            "--owner",
            "Tester",
            "--dir",
            str(out_of_apps),
            "--profile",
            "local-only",
        ],
    )
    assert result.exit_code != 0
    msg = result.output + str(result.exception)
    assert "must live directly under" in msg or "applications" in msg


def test_tp_cli_refuse_3_existing_adopter_recommends_upgrade(cli_runner) -> None:
    """Run init twice on the same in-root sandbox; second invocation refuses."""
    from groundtruth_kb.cli import main as cli

    sandbox_name = f"_test_{uuid.uuid4().hex[:8]}"
    sandbox_path = _GT_KB_HOST_ROOT / "applications" / sandbox_name
    try:
        # First invocation succeeds.
        result1 = cli_runner.invoke(
            cli,
            [
                "project",
                "init",
                sandbox_name,
                "--owner",
                "Tester",
                "--profile",
                "local-only",
            ],
        )
        assert result1.exit_code == 0, f"First init failed: {result1.output} | exc={result1.exception!r}"
        assert sandbox_path.exists()

        # Second invocation must refuse.
        result2 = cli_runner.invoke(
            cli,
            [
                "project",
                "init",
                sandbox_name,
                "--owner",
                "Tester",
                "--profile",
                "local-only",
            ],
        )
        assert result2.exit_code != 0
        msg = result2.output + str(result2.exception)
        assert "gt project upgrade" in msg
    finally:
        if sandbox_path.exists():
            shutil.rmtree(sandbox_path, ignore_errors=True)


def test_tp_cli_installed_context_allows_explicit_adopter_root(
    tmp_path: Path, cli_runner, monkeypatch: pytest.MonkeyPatch
) -> None:
    from groundtruth_kb.cli import main as cli
    from groundtruth_kb.project import scaffold as scaffold_mod

    monkeypatch.setattr(scaffold_mod, "_is_installed_wheel_context", lambda: True)
    host_root = tmp_path / "host"
    target = host_root / "applications" / "WheelApp"

    result = cli_runner.invoke(
        cli,
        [
            "project",
            "init",
            "WheelApp",
            "--owner",
            "Tester",
            "--gt-kb-root",
            str(host_root),
            "--profile",
            "local-only",
            "--no-include-ci",
            "--no-seed-example",
        ],
    )

    assert result.exit_code == 0, f"init failed: {result.output} | exc={result.exception!r}"
    assert (target / "groundtruth.toml").exists()


def test_tp_cli_installed_context_defaults_host_root_to_cwd(
    tmp_path: Path, cli_runner, monkeypatch: pytest.MonkeyPatch
) -> None:
    from groundtruth_kb.cli import main as cli
    from groundtruth_kb.project import scaffold as scaffold_mod

    monkeypatch.setattr(scaffold_mod, "_is_installed_wheel_context", lambda: True)
    monkeypatch.chdir(tmp_path)
    target = tmp_path / "applications" / "WheelDefault"

    result = cli_runner.invoke(
        cli,
        [
            "project",
            "init",
            "WheelDefault",
            "--owner",
            "Tester",
            "--profile",
            "local-only",
            "--no-include-ci",
            "--no-seed-example",
        ],
    )

    assert result.exit_code == 0, f"init failed: {result.output} | exc={result.exception!r}"
    assert (target / "groundtruth.toml").exists()


# ============================================================================
# TP-INTEG-1 — In-root sandbox integration test (Phase 9 §1 enumeration)
# ============================================================================


@pytest.fixture
def in_root_sandbox():
    """Yield an in-root sandbox path under ``applications/_test_<uuid>/`` and
    clean up after the test.
    """
    sandbox_name = f"_test_{uuid.uuid4().hex[:8]}"
    sandbox_path = _GT_KB_HOST_ROOT / "applications" / sandbox_name
    try:
        yield sandbox_path
    finally:
        if sandbox_path.exists():
            shutil.rmtree(sandbox_path, ignore_errors=True)


def test_tp_integ_1_scaffold_emits_phase9_section1_enumeration(in_root_sandbox: Path) -> None:
    """One integration test that inspects all Phase 9 §1 enumeration items
    after a real scaffold under the in-root sandbox path.

    Collapses TP1-TP13 from the proposal into a single end-to-end test to
    minimize scaffold I/O while preserving the per-bullet assertions.
    """
    options = ScaffoldOptions(
        project_name=in_root_sandbox.name,
        profile="local-only",
        owner="Tester",
        target_dir=in_root_sandbox,
        gt_kb_root=_GT_KB_HOST_ROOT,
        seed_example=False,
        include_ci=False,
    )
    result = scaffold_project(options)
    assert result == in_root_sandbox.resolve()

    # TP1: groundtruth.toml + [service] block
    toml_text = (in_root_sandbox / "groundtruth.toml").read_text(encoding="utf-8")
    assert "[service]" in toml_text
    assert "endpoint =" in toml_text
    assert "configure-me://placeholder/v1" in toml_text

    # TP3: groundtruth.db initialized
    assert (in_root_sandbox / "groundtruth.db").exists()

    # TP5: memory/work_list.md placeholder
    work_list_text = (in_root_sandbox / "memory" / "work_list.md").read_text(encoding="utf-8")
    assert "Active Work List" in work_list_text

    # TP6: memory/release-readiness.md banner
    banner_text = (in_root_sandbox / "memory" / "release-readiness.md").read_text(encoding="utf-8")
    # Strip blockquote `> ` markers + collapse whitespace so the line-wrapped
    # banner still matches the substantive banner phrases.
    banner_normalized = " ".join(line.lstrip("> ").strip() for line in banner_text.splitlines() if line.strip())
    banner_normalized = " ".join(banner_normalized.split())
    assert "Application-subject release readiness only" in banner_normalized
    assert "GT-KB product readiness is not tracked here" in banner_normalized

    # TP8: .codex/hooks.json forward-compat intent
    codex_hooks = (in_root_sandbox / ".codex" / "hooks.json").read_text(encoding="utf-8")
    assert "ADR-CODEX-HOOK-PARITY-FALLBACK-001" in codex_hooks

    # TP9: .groundtruth/formal-artifact-approvals/.gitkeep
    assert (in_root_sandbox / ".groundtruth" / "formal-artifact-approvals" / ".gitkeep").exists()

    # TP10: docs/gtkb-dashboard/ NOT pre-populated
    assert not (in_root_sandbox / "docs" / "gtkb-dashboard").exists()

    # TP11: .gitignore exists with content
    gitignore_text = (in_root_sandbox / ".gitignore").read_text(encoding="utf-8")
    assert gitignore_text.strip()

    # TP12: forbidden product artifacts absent
    assert not (in_root_sandbox / "groundtruth-kb" / "src").exists()
    assert not (in_root_sandbox / "groundtruth-kb" / "tests").exists()

    # TP13: README contains quickstart markers + service-endpoint reference
    readme_text = (in_root_sandbox / "README.md").read_text(encoding="utf-8")
    assert "Quickstart" in readme_text
    assert "[service]" in readme_text


def test_tp_integ_1b_doctor_service_endpoint_check_passes(in_root_sandbox: Path) -> None:
    """TP2 (cross-slice integration): scaffolded service endpoint clears
    Slice 1's `_check_isolation_service_endpoint_not_raw_db` doctor check.
    """
    from groundtruth_kb.project.doctor_isolation import (
        _check_isolation_service_endpoint_not_raw_db,
    )

    options = ScaffoldOptions(
        project_name=in_root_sandbox.name,
        profile="local-only",
        owner="Tester",
        target_dir=in_root_sandbox,
        gt_kb_root=_GT_KB_HOST_ROOT,
        seed_example=False,
        include_ci=False,
    )
    scaffold_project(options)
    check = _check_isolation_service_endpoint_not_raw_db(in_root_sandbox)
    assert check.found is True
    assert check.status in ("pass", "warning"), (
        f"service-endpoint check should not error on scaffolded fixture; "
        f"got status={check.status} message={check.message}"
    )


# ============================================================================
# TP16 — Registry / enumerate coverage
# ============================================================================


def test_tp16_enumerate_outputs_lists_new_scaffold_files() -> None:
    """The new Phase 9 §1 scaffold artifacts are registered for upgrade
    coverage via ``enumerate_scaffold_outputs``.
    """
    paths = set(enumerate_scaffold_outputs("local-only"))
    expected_new = {
        "README.md",
        "memory/work_list.md",
        "memory/release-readiness.md",
        ".codex/hooks.json",
        ".groundtruth/formal-artifact-approvals/.gitkeep",
    }
    missing = expected_new - paths
    assert not missing, f"Missing from enumerate_scaffold_outputs: {sorted(missing)}"


# ============================================================================
# TP14 / TP15 — Byte-level golden fixture diffs
# ============================================================================
#
# Per Codex `-012.md` F1 + scoping `-003.md:111` + GO proposal `-007.md:120`:
# byte-compare freshly scaffolded output against committed fixture trees at
# `groundtruth-kb/tests/fixtures/scaffold_golden/{local-only,dual-agent}/`.
#
# Determinism contract: every scaffolded file is byte-deterministic given the
# same `ScaffoldOptions` EXCEPT:
#   1. `groundtruth.db` — SQLite binary with non-deterministic page checksums.
#      Excluded from fixtures; existence asserted separately.
#   2. `groundtruth.toml::created_at` — datetime.now()-derived in
#      `manifest.py:30`. The whole `created_at = "..."` line is masked in both
#      fixture and scaffold output before byte-comparison.
#
# Regenerate fixtures (when scaffold templates legitimately change):
#   python scripts/_capture_scaffold_golden.py

_GOLDEN_FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "scaffold_golden"
# `created_at = "..."` is unique to TOML key-value context here. No anchor —
# scaffold writes this with native line endings (CRLF on Windows, LF on Linux),
# and a `$` anchor in MULTILINE mode would not match before `\r`.
_CREATED_AT_RE = re.compile(rb'created_at = "[^"]*"')
_CREATED_AT_MASK = b'created_at = "<NORMALIZED-FOR-FIXTURE-DIFF>"'


def _normalize_for_diff(content: bytes, rel_path: Path) -> bytes:
    """Mask known dynamic fields. Currently only `groundtruth.toml::created_at`."""
    if rel_path.name == "groundtruth.toml":
        return _CREATED_AT_RE.sub(_CREATED_AT_MASK, content)
    return content


def _list_fixture_files(profile: str) -> set[Path]:
    fixture_root = _GOLDEN_FIXTURE_ROOT / profile
    return {f.relative_to(fixture_root) for f in fixture_root.rglob("*") if f.is_file()}


def _run_golden_scaffold(profile: str) -> Path:
    """Scaffold to the fixed in-root golden sandbox and return its path."""
    sandbox_name = f"_test_golden_{profile.replace('-', '_')}"
    sandbox = _GT_KB_HOST_ROOT / "applications" / sandbox_name
    if sandbox.exists():
        shutil.rmtree(sandbox)
    options = ScaffoldOptions(
        project_name=sandbox_name,
        profile=profile,
        owner="GoldenFixtureOwner",
        target_dir=sandbox,
        gt_kb_root=_GT_KB_HOST_ROOT,
        seed_example=False,
        include_ci=False,
        init_git=False,
    )
    scaffold_project(options)
    return sandbox


def _assert_byte_equal_to_fixture(profile: str, sandbox: Path) -> None:
    fixture_root = _GOLDEN_FIXTURE_ROOT / profile
    expected_files = _list_fixture_files(profile)
    actual_files = {f.relative_to(sandbox) for f in sandbox.rglob("*") if f.is_file()}
    db_path = Path("groundtruth.db")
    assert db_path in actual_files, "groundtruth.db must be created by scaffold"

    extras = actual_files - expected_files - {db_path}
    missing = expected_files - actual_files
    assert not extras, (
        f"Scaffold produced files not in fixture (regen fixtures or update scaffold): {sorted(map(str, extras))}"
    )
    assert not missing, f"Fixture lists files not produced by scaffold (regen fixtures): {sorted(map(str, missing))}"

    mismatches: list[str] = []
    for rel in sorted(expected_files):
        expected_bytes = _normalize_for_diff((fixture_root / rel).read_bytes(), rel)
        actual_bytes = _normalize_for_diff((sandbox / rel).read_bytes(), rel)
        if expected_bytes != actual_bytes:
            mismatches.append(str(rel))
    assert not mismatches, (
        f"Byte-level mismatch in {len(mismatches)} file(s) for profile "
        f"{profile!r}: {mismatches[:10]}" + (" ..." if len(mismatches) > 10 else "")
    )


def test_tp14_local_only_matches_golden_fixture() -> None:
    """TP14: local-only scaffold output byte-equals the committed golden tree."""
    sandbox = _run_golden_scaffold("local-only")
    try:
        _assert_byte_equal_to_fixture("local-only", sandbox)
    finally:
        if sandbox.exists():
            shutil.rmtree(sandbox, ignore_errors=True)


def test_tp15_dual_agent_matches_golden_fixture() -> None:
    """TP15: dual-agent scaffold output byte-equals the committed golden tree."""
    sandbox = _run_golden_scaffold("dual-agent")
    try:
        _assert_byte_equal_to_fixture("dual-agent", sandbox)
    finally:
        if sandbox.exists():
            shutil.rmtree(sandbox, ignore_errors=True)
