"""Tests for the WI-4528 sweep-commit protected-hook co-stage planning helper.

Per ``bridge/gtkb-wi4528-sweep-commit-protected-hook-co-stage-helper-001.md``
(NEW) and ``-002`` (Codex GO). Covers the eight acceptance criteria in the
proposal's Verification Plan, including the 2026-06-13 incident regression.
WI-4709 extends the same planner with a non-terminal bridge-thread hold so
protected paths cannot be committed ahead of VERIFIED. WI-4710 adds the
stricter staged-evidence rule: co-staged bridge evidence only clears a protected
path when that evidence's thread is latest VERIFIED.

The fixture bridge filenames used below (``bridge/wi4528-fixture-*.md``) are
synthetic test fixtures created on disk inside ``tmp_path``; they are NOT
citations to live bridge threads. They never appear in the bridge/report text
for this thread.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import dataclasses
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import sweep_commit_helpers as helper  # noqa: E402

# A minimal inventory-drift TOML matching the real schema: one co-staged-evidence
# entry (hook-and-action-gates, accept=false) and one baseline-update entry
# (accept=true) that MUST be excluded from the protected globs.
_DEFAULT_TOML = """\
schema_version = 1

[[protected_artifacts]]
id = "hook-and-action-gates"
patterns = [
  ".claude/hooks/**",
  ".codex/hooks.json",
  ".githooks/**",
]
severity = "compatibility_tests"
route = "compatibility_tests"
accept_with_inventory_baseline_update = false
required_evidence = ["hook parity test", "compatibility tests"]

[[protected_artifacts]]
id = "inventory-collector-and-baseline"
patterns = [
  "scripts/check_dev_environment_inventory_drift.py",
]
severity = "accepted_baseline_update"
route = "accepted_baseline_update"
accept_with_inventory_baseline_update = true
required_evidence = ["inventory regenerated", "normalized drift check"]
"""


def _make_project(
    tmp_path: Path, *, toml_text: str | None = _DEFAULT_TOML, bridge_files: dict[str, str] | None = None
) -> Path:
    """Build a fake project root with the inventory-drift TOML and bridge files.

    ``toml_text=None`` omits the TOML entirely (fail-soft case).
    ``bridge_files`` maps relative ``bridge/<name>.md`` paths to body content.
    """
    root = tmp_path / "proj"
    root.mkdir()
    if toml_text is not None:
        toml_path = root / helper.INVENTORY_DRIFT_TOML_RELATIVE_PATH
        toml_path.parent.mkdir(parents=True, exist_ok=True)
        toml_path.write_text(toml_text, encoding="utf-8")
    if bridge_files:
        for rel, body in bridge_files.items():
            bf = root / rel
            bf.parent.mkdir(parents=True, exist_ok=True)
            bf.write_text(body, encoding="utf-8")
    return root


def _batch_of_kind(batches: list[helper.CommitBatch], kind: str) -> list[helper.CommitBatch]:
    return [b for b in batches if b.kind == kind]


# ---------------------------------------------------------------------------
# AC1 (WI-4528 root): protected hook-config + co-staged bridge evidence -> SAME batch.
# ---------------------------------------------------------------------------
def test_protected_hook_with_bridge_evidence_grouped(tmp_path: Path) -> None:
    bridge_rel = "bridge/wi4528-fixture-hooks-001.md"
    root = _make_project(
        tmp_path,
        bridge_files={bridge_rel: "VERIFIED\n\nThis report registers a Stop hook in .codex/hooks.json.\n"},
    )
    staged = [".codex/hooks.json", bridge_rel]

    batches = helper.plan_commit_batches(staged, root)

    pwe = _batch_of_kind(batches, "protected-with-evidence")
    assert len(pwe) == 1
    assert set(pwe[0].paths) == {".codex/hooks.json", bridge_rel}
    assert bridge_rel in pwe[0].evidence
    # Nothing should be flagged missing-evidence.
    assert _batch_of_kind(batches, "protected-missing-evidence") == []


# ---------------------------------------------------------------------------
# AC2 (2026-06-13 incident regression): protected hook with NO bridge evidence ->
# clear missing-evidence diagnostic.
# ---------------------------------------------------------------------------
def test_missing_evidence_diagnostic(tmp_path: Path) -> None:
    root = _make_project(tmp_path)
    staged = [".codex/hooks.json"]

    batches = helper.plan_commit_batches(staged, root)

    missing = _batch_of_kind(batches, "protected-missing-evidence")
    assert len(missing) == 1
    assert missing[0].paths == [".codex/hooks.json"]
    assert "blocked by the inventory-drift gate" in missing[0].rationale
    # No false protected-with-evidence batch.
    assert _batch_of_kind(batches, "protected-with-evidence") == []


# ---------------------------------------------------------------------------
# AC3: non-numbered bridge files are not review evidence for the gate.
# ---------------------------------------------------------------------------
def test_index_md_is_not_review_evidence(tmp_path: Path) -> None:
    root = _make_project(tmp_path)
    staged = [".codex/hooks.json", "bridge/INDEX.md"]

    batches = helper.plan_commit_batches(staged, root)

    assert _batch_of_kind(batches, "protected-with-evidence") == []
    missing = _batch_of_kind(batches, "protected-missing-evidence")
    assert len(missing) == 1
    assert missing[0].paths == [".codex/hooks.json"]
    unconstrained = _batch_of_kind(batches, "unconstrained")
    assert len(unconstrained) == 1
    assert unconstrained[0].paths == ["bridge/INDEX.md"]


# ---------------------------------------------------------------------------
# AC4: bridge-only files batch separately when not tied to a protected path.
# ---------------------------------------------------------------------------
def test_unrelated_bridge_files_separate_batch(tmp_path: Path) -> None:
    bridge_rel = "bridge/wi4528-fixture-unrelated-001.md"
    root = _make_project(
        tmp_path,
        bridge_files={bridge_rel: "NEW\n\nUnrelated proposal, cites nothing protected.\n"},
    )
    staged = [bridge_rel, "scripts/x.py"]

    batches = helper.plan_commit_batches(staged, root)

    bridge_only = _batch_of_kind(batches, "bridge-only")
    unconstrained = _batch_of_kind(batches, "unconstrained")
    assert len(bridge_only) == 1
    assert bridge_only[0].paths == [bridge_rel]
    assert len(unconstrained) == 1
    assert unconstrained[0].paths == ["scripts/x.py"]
    # No protected batches at all.
    assert _batch_of_kind(batches, "protected-with-evidence") == []
    assert _batch_of_kind(batches, "protected-missing-evidence") == []


# ---------------------------------------------------------------------------
# AC5: multiple protected paths each pair with their own evidence.
# ---------------------------------------------------------------------------
def test_multiple_protected_paths_each_get_evidence(tmp_path: Path) -> None:
    bridge_a = "bridge/wi4528-fixture-codex-001.md"
    bridge_b = "bridge/wi4528-fixture-claude-001.md"
    root = _make_project(
        tmp_path,
        bridge_files={
            bridge_a: "VERIFIED\n\nRegisters .codex/hooks.json Stop hook.\n",
            bridge_b: "VERIFIED\n\nAdds .claude/hooks/foo.py PreToolUse gate.\n",
        },
    )
    staged = [".codex/hooks.json", ".claude/hooks/foo.py", bridge_a, bridge_b]

    batches = helper.plan_commit_batches(staged, root)

    pwe = _batch_of_kind(batches, "protected-with-evidence")
    assert len(pwe) == 2
    by_protected = {next(p for p in b.paths if not p.startswith("bridge/")): b for b in pwe}
    assert set(by_protected[".codex/hooks.json"].evidence) == {bridge_a}
    assert set(by_protected[".claude/hooks/foo.py"].evidence) == {bridge_b}
    # Each bridge file is consumed as evidence, so no leftover bridge-only batch.
    assert _batch_of_kind(batches, "bridge-only") == []


# ---------------------------------------------------------------------------
# AC6: protected globs read declaratively from the inventory-drift TOML.
# ---------------------------------------------------------------------------
def test_protected_globs_read_from_toml(tmp_path: Path) -> None:
    custom_toml = """\
schema_version = 1

[[protected_artifacts]]
id = "new-protected-surface"
patterns = ["config/new-protected/**"]
accept_with_inventory_baseline_update = false
required_evidence = ["bridge report"]
"""
    root = _make_project(tmp_path, toml_text=custom_toml)

    globs = helper.load_protected_path_globs(root)
    assert "config/new-protected/**" in globs
    assert helper.is_protected_path("config/new-protected/thing.toml", globs) is True
    # A path outside the new glob is not protected.
    assert helper.is_protected_path("scripts/other.py", globs) is False


def test_baseline_update_entries_excluded_from_protected_globs(tmp_path: Path) -> None:
    """accept_with_inventory_baseline_update=true entries do NOT require co-staged evidence."""
    root = _make_project(tmp_path)
    globs = helper.load_protected_path_globs(root)
    # hook entry (accept=false) is included; baseline-update entry (accept=true) is not.
    assert ".codex/hooks.json" in globs
    assert "scripts/check_dev_environment_inventory_drift.py" not in globs


# ---------------------------------------------------------------------------
# AC7: fail-soft when TOML missing (no commit-blocking exception).
# ---------------------------------------------------------------------------
def test_fail_soft_when_toml_missing(tmp_path: Path) -> None:
    root = _make_project(tmp_path, toml_text=None)
    staged = [".codex/hooks.json", "bridge/INDEX.md", "scripts/x.py"]

    # load_protected_path_globs returns [] rather than raising.
    assert helper.load_protected_path_globs(root) == []

    batches = helper.plan_commit_batches(staged, root)
    assert len(batches) == 1
    assert batches[0].kind == "unconstrained"
    assert set(batches[0].paths) == set(staged)
    assert batches[0].rationale.startswith("WARN")


def test_fail_soft_when_toml_malformed(tmp_path: Path) -> None:
    """A malformed TOML must not raise; it degrades to the fail-soft unconstrained plan."""
    root = _make_project(tmp_path, toml_text="this is = = not valid toml [[[")
    assert helper.load_protected_path_globs(root) == []
    batches = helper.plan_commit_batches([".codex/hooks.json"], root)
    assert len(batches) == 1
    assert batches[0].kind == "unconstrained"


# ---------------------------------------------------------------------------
# AC8: real-world replay of the 2026-06-13 incident staged set.
# ---------------------------------------------------------------------------
def test_real_world_2026_06_13_incident_replay_active_go_is_held(tmp_path: Path) -> None:
    """The 2026-06-13 split: the .codex/hooks.json change had no co-staged bridge.

    With WI-4709, a GO thread that still cites the hooks file is active and
    non-terminal, so the hooks file is held rather than committed with evidence.
    The settings.json + lint-script + tests still land unconstrained.
    """
    bridge_rel = "bridge/wi4528-fixture-grilling-gate-001.md"
    root = _make_project(
        tmp_path,
        bridge_files={bridge_rel: "GO\n\nWI-3446 grilling gate: registers the Stop hook in .codex/hooks.json.\n"},
    )
    # The actual incident file list (hooks file + its bridge evidence + the
    # non-protected files committed separately at 41727a5ec).
    staged = [
        ".codex/hooks.json",
        bridge_rel,
        ".claude/settings.json",
        "scripts/check_lo_advisory_grilling_gate.py",
        "platform_tests/scripts/test_advisory_grilling_gate_lint.py",
    ]

    batches = helper.plan_commit_batches(staged, root)

    held = _batch_of_kind(batches, "protected-unverified-thread")
    assert len(held) == 1
    assert held[0].paths == [".codex/hooks.json"]
    assert "wi4528-fixture-grilling-gate@GO" in held[0].rationale
    assert "not VERIFIED" in held[0].rationale
    assert _batch_of_kind(batches, "protected-with-evidence") == []
    bridge_only = _batch_of_kind(batches, "bridge-only")
    assert len(bridge_only) == 1
    assert bridge_only[0].paths == [bridge_rel]
    # .claude/settings.json is NOT in the protected registry (only .claude/hooks/**),
    # so it lands unconstrained, not blocked.
    unconstrained = _batch_of_kind(batches, "unconstrained")
    assert len(unconstrained) == 1
    assert set(unconstrained[0].paths) == {
        ".claude/settings.json",
        "scripts/check_lo_advisory_grilling_gate.py",
        "platform_tests/scripts/test_advisory_grilling_gate_lint.py",
    }
    # No missing-evidence: the hooks file is held by active bridge state instead.
    assert _batch_of_kind(batches, "protected-missing-evidence") == []


# ---------------------------------------------------------------------------
# WI-4709: active non-terminal bridge threads hold protected paths until VERIFIED.
# ---------------------------------------------------------------------------
def test_protected_path_in_nonterminal_thread_is_held(tmp_path: Path) -> None:
    bridge_rel = "bridge/wi4709-active-001.md"
    root = _make_project(
        tmp_path,
        bridge_files={bridge_rel: "REVISED\n\nUpdates .claude/hooks/foo.py for the active thread.\n"},
    )
    staged = [".claude/hooks/foo.py", bridge_rel]

    batches = helper.plan_commit_batches(staged, root)

    held = _batch_of_kind(batches, "protected-unverified-thread")
    assert len(held) == 1
    assert held[0].paths == [".claude/hooks/foo.py"]
    assert "wi4709-active@REVISED" in held[0].rationale
    assert _batch_of_kind(batches, "protected-with-evidence") == []
    bridge_only = _batch_of_kind(batches, "bridge-only")
    assert len(bridge_only) == 1
    assert bridge_only[0].paths == [bridge_rel]


def test_protected_path_with_only_verified_thread_commits(tmp_path: Path) -> None:
    bridge_001 = "bridge/wi4709-verified-001.md"
    bridge_002 = "bridge/wi4709-verified-002.md"
    root = _make_project(
        tmp_path,
        bridge_files={
            bridge_001: "NEW\n\nInitial proposal for .codex/hooks.json.\n",
            bridge_002: "VERIFIED\n\nVerified implementation for .codex/hooks.json.\n",
        },
    )
    staged = [".codex/hooks.json", bridge_002]

    batches = helper.plan_commit_batches(staged, root)

    assert _batch_of_kind(batches, "protected-active-thread-nonterminal") == []
    pwe = _batch_of_kind(batches, "protected-with-evidence")
    assert len(pwe) == 1
    assert set(pwe[0].paths) == {".codex/hooks.json", bridge_002}


def test_latest_version_status_decides_not_earlier_version(tmp_path: Path) -> None:
    terminal_bridge = "bridge/wi4709-terminal-002.md"
    active_bridge = "bridge/wi4709-active-latest-002.md"
    root = _make_project(
        tmp_path,
        bridge_files={
            "bridge/wi4709-terminal-001.md": "NEW\n\nInitial .codex/hooks.json proposal.\n",
            terminal_bridge: "VERIFIED\n\nVerified .codex/hooks.json implementation.\n",
            "bridge/wi4709-active-latest-001.md": "GO\n\nApproved .claude/hooks/foo.py change.\n",
            active_bridge: "REVISED\n\nStill active .claude/hooks/foo.py revision.\n",
        },
    )
    staged = [".codex/hooks.json", terminal_bridge, ".claude/hooks/foo.py", active_bridge]

    batches = helper.plan_commit_batches(staged, root)

    held = _batch_of_kind(batches, "protected-unverified-thread")
    assert len(held) == 1
    assert held[0].paths == [".claude/hooks/foo.py"]
    assert "wi4709-active-latest@REVISED" in held[0].rationale
    pwe = _batch_of_kind(batches, "protected-with-evidence")
    assert len(pwe) == 1
    assert set(pwe[0].paths) == {".codex/hooks.json", terminal_bridge}


def test_protected_path_with_no_citing_thread_unaffected(tmp_path: Path) -> None:
    evidence_bridge = "bridge/wi4709-evidence-002.md"
    active_unrelated = "bridge/wi4709-unrelated-001.md"
    root = _make_project(
        tmp_path,
        bridge_files={
            evidence_bridge: "VERIFIED\n\nVerified .codex/hooks.json implementation.\n",
            active_unrelated: "REVISED\n\nThis active thread cites no protected hook path.\n",
        },
    )
    staged = [".codex/hooks.json", evidence_bridge]

    batches = helper.plan_commit_batches(staged, root)

    assert _batch_of_kind(batches, "protected-active-thread-nonterminal") == []
    pwe = _batch_of_kind(batches, "protected-with-evidence")
    assert len(pwe) == 1
    assert set(pwe[0].paths) == {".codex/hooks.json", evidence_bridge}


def test_nonterminal_gate_fail_soft_when_bridge_dir_absent(tmp_path: Path) -> None:
    root = _make_project(tmp_path)
    staged = [".codex/hooks.json"]

    assert helper.active_nonterminal_bridge_threads_citing(staged, root) == {".codex/hooks.json": []}

    batches = helper.plan_commit_batches(staged, root)
    assert _batch_of_kind(batches, "protected-active-thread-nonterminal") == []
    missing = _batch_of_kind(batches, "protected-missing-evidence")
    assert len(missing) == 1
    assert missing[0].paths == [".codex/hooks.json"]


def test_codex_hooks_json_in_nonterminal_thread_is_held(tmp_path: Path) -> None:
    bridge_rel = "bridge/wi4709-codex-hooks-001.md"
    root = _make_project(
        tmp_path,
        bridge_files={bridge_rel: "NEW\n\nRegisters the Codex hook file at .codex/hooks.json.\n"},
    )
    staged = [".codex/hooks.json", bridge_rel]

    batches = helper.plan_commit_batches(staged, root)

    held = _batch_of_kind(batches, "protected-unverified-thread")
    assert len(held) == 1
    assert held[0].paths == [".codex/hooks.json"]
    assert "wi4709-codex-hooks@NEW" in held[0].rationale
    assert _batch_of_kind(batches, "protected-with-evidence") == []


# ---------------------------------------------------------------------------
# WI-4710: co-staged bridge evidence only clears protected paths after VERIFIED.
# ---------------------------------------------------------------------------
def test_protected_path_with_unverified_thread_is_withheld(tmp_path: Path) -> None:
    bridge_rel = "bridge/wi4710-unverified-001.md"
    root = _make_project(
        tmp_path,
        bridge_files={bridge_rel: "NEW\n\nUpdates .claude/hooks/foo.py before verification.\n"},
    )
    staged = [".claude/hooks/foo.py", bridge_rel]

    batches = helper.plan_commit_batches(staged, root)

    held = _batch_of_kind(batches, "protected-unverified-thread")
    assert len(held) == 1
    assert held[0].paths == [".claude/hooks/foo.py"]
    assert held[0].evidence == [bridge_rel]
    assert "wi4710-unverified@NEW" in held[0].rationale
    assert _batch_of_kind(batches, "protected-with-evidence") == []


def test_unverified_thread_batch_rationale_instructs_exclusion(tmp_path: Path) -> None:
    bridge_rel = "bridge/wi4710-nogo-002.md"
    root = _make_project(
        tmp_path,
        bridge_files={
            "bridge/wi4710-nogo-001.md": "NEW\n\nInitial .codex/hooks.json proposal.\n",
            bridge_rel: "NO-GO\n\nStill cites .codex/hooks.json.\n",
        },
    )
    staged = [".codex/hooks.json", bridge_rel]

    batches = helper.plan_commit_batches(staged, root)

    held = _batch_of_kind(batches, "protected-unverified-thread")
    assert len(held) == 1
    assert "exclude the protected path from sweep" in held[0].rationale
    assert "until the bridge thread reaches VERIFIED" in held[0].rationale


def test_unreadable_thread_status_treated_as_unverified(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    bridge_rel = "bridge/wi4710-unreadable-001.md"
    root = _make_project(
        tmp_path,
        bridge_files={bridge_rel: "VERIFIED\n\nMentions .codex/hooks.json.\n"},
    )

    def _raise_oserror(project_root: Path) -> dict[str, object]:
        raise OSError("simulated scan failure")

    monkeypatch.setattr(helper, "scan_expected_documents", _raise_oserror)

    batches = helper.plan_commit_batches([".codex/hooks.json", bridge_rel], root)

    held = _batch_of_kind(batches, "protected-unverified-thread")
    assert len(held) == 1
    assert held[0].paths == [".codex/hooks.json"]
    assert f"{bridge_rel}@unreadable" in held[0].rationale
    assert _batch_of_kind(batches, "protected-with-evidence") == []


def test_wi4682_incident_replay_withholds_protected_rule_files(tmp_path: Path) -> None:
    custom_toml = """\
schema_version = 1

[[protected_artifacts]]
id = "protected-narrative-rules"
patterns = [".claude/rules/**"]
accept_with_inventory_baseline_update = false
required_evidence = ["bridge report"]
"""
    bridge_rel = "bridge/gtkb-wi4682-automation-value-cost-principle-015.md"
    root = _make_project(
        tmp_path,
        toml_text=custom_toml,
        bridge_files={bridge_rel: "REVISED\n\nImplementation report for .claude/rules/bridge-essential.md.\n"},
    )
    staged = [".claude/rules/bridge-essential.md", bridge_rel]

    batches = helper.plan_commit_batches(staged, root)

    held = _batch_of_kind(batches, "protected-unverified-thread")
    assert len(held) == 1
    assert held[0].paths == [".claude/rules/bridge-essential.md"]
    assert "gtkb-wi4682-automation-value-cost-principle@REVISED" in held[0].rationale
    assert _batch_of_kind(batches, "protected-with-evidence") == []


def test_non_protected_paths_unaffected_by_thread_gate(tmp_path: Path) -> None:
    bridge_rel = "bridge/wi4710-source-001.md"
    root = _make_project(
        tmp_path,
        bridge_files={bridge_rel: "NEW\n\nMentions scripts/source.py while active.\n"},
    )
    staged = ["scripts/source.py", bridge_rel]

    batches = helper.plan_commit_batches(staged, root)

    assert _batch_of_kind(batches, "protected-unverified-thread") == []
    bridge_only = _batch_of_kind(batches, "bridge-only")
    unconstrained = _batch_of_kind(batches, "unconstrained")
    assert len(bridge_only) == 1
    assert bridge_only[0].paths == [bridge_rel]
    assert len(unconstrained) == 1
    assert unconstrained[0].paths == ["scripts/source.py"]


# ---------------------------------------------------------------------------
# Supporting unit checks for the smaller API surface.
# ---------------------------------------------------------------------------
def test_partition_staged_buckets(tmp_path: Path) -> None:
    root = _make_project(tmp_path)
    globs = helper.load_protected_path_globs(root)
    parts = helper.partition_staged(
        [".codex/hooks.json", "bridge/INDEX.md", "bridge/x-001.md", "scripts/y.py"],
        globs,
    )
    assert parts["protected"] == [".codex/hooks.json"]
    assert parts["bridge"] == ["bridge/x-001.md"]
    assert parts["other"] == ["bridge/INDEX.md", "scripts/y.py"]


def test_is_bridge_evidence_path() -> None:
    assert helper.is_bridge_evidence_path("bridge/INDEX.md") is False
    assert helper.is_bridge_evidence_path("bridge/anything-001.md") is True
    assert helper.is_bridge_evidence_path("scripts/x.py") is False


def test_windows_backslash_paths_normalized(tmp_path: Path) -> None:
    """Staged paths reported with backslashes are normalized before matching."""
    root = _make_project(tmp_path)
    globs = helper.load_protected_path_globs(root)
    assert helper.is_protected_path(r".codex\hooks.json", globs) is True


def test_commit_batch_is_frozen() -> None:
    batch = helper.CommitBatch(paths=["a"], kind="unconstrained")
    with pytest.raises(dataclasses.FrozenInstanceError):
        batch.kind = "other"  # type: ignore[misc]
