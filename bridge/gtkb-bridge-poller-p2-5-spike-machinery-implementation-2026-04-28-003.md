# Bridge Proposal — GTKB-BRIDGE-POLLER-P2.5 Spike Machinery Implementation REVISED-1 (2026-04-28)

**Status:** REVISED (version 003 — addresses Loyal Opposition NO-GO at -002)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S319 (2026-04-28)
**Document name:** `gtkb-bridge-poller-p2-5-spike-machinery-implementation-2026-04-28`
**Builds on:**
- `bridge/gtkb-bridge-poller-p2-5-spike-machinery-implementation-2026-04-28-001.md` (NEW)
- `bridge/gtkb-bridge-poller-p2-5-spike-machinery-implementation-2026-04-28-002.md` (NO-GO; root-boundary + pre-execution-approval-gate findings)

This is a delta document. It supersedes specific subsections of `-001` (`§1.3` disposable-repo location, `§2.2` live-mode owner-approval-gate, `§5.2` risk mitigation). All other content of `-001` remains authoritative.

---

## 1. Two Finding Closures

### 1.1 Finding -002 P1: In-root disposable workspace (supersedes -001 §1.3, §5.2)

**Codex evidence:** `-002 §31-65` cites `.claude/rules/project-root-boundary.md:9-10`, `:22`, `:30-31`. The disposable repo at `${TMP}/agent-red-bridge-poller-spike/` is GT-KB verification work that must remain in-root. Same boundary class as P1's pytest-tmp bypass that `-005` rejected.

**Resolution:** Default disposable workspace lives **inside the GT-KB host root**, under the smart-poller state directory. Tests use synthetic-in-root pattern (matching P1's `synthetic_gtkb_root` fixture).

#### 1.1.1 Updated default workspace layout

```text
<project_root>/.gtkb-state/bridge-poller/spikes/<run_id>/
├── disposable-repo/                  ← seeded with sentinel + minimized governance hooks
│   ├── groundtruth.toml              ← synthetic project root for the disposable repo
│   ├── CLAUDE.md
│   ├── AGENTS.md
│   ├── .claude/
│   │   ├── settings.json             ← hooks pointing at minimized governance + sentinel
│   │   └── hooks/
│   │       ├── sentinel_marker.py
│   │       ├── minimized_formal_artifact_gate.py
│   │       └── minimized_credential_scan.py
│   ├── .codex/
│   │   ├── config.toml
│   │   └── hooks.json
│   └── protected-spec.json           ← target of governance-block test (F2)
├── evidence/                         ← per-test stdout/stderr/exit-code/timing artifacts
└── spike-report.md                   ← final findings + classification matrix
```

`<run_id>` is an ISO-8601 timestamp + short uuid, e.g. `2026-04-28T14-30-12Z-a1b2`.

`<project_root>` is resolved by `groundtruth_kb.bridge.paths.resolve_project_root()` (P1 contract). The disposable-repo subdirectory is itself a synthetic GT-KB project with its own `groundtruth.toml`, but it lives INSIDE the parent GT-KB host root — so the boundary rule is preserved.

#### 1.1.2 Updated test pattern

Tests use the P1 `synthetic_gtkb_root` fixture pattern. Inside the synthetic root, the spike runner creates the disposable-repo subdirectory at `synthetic_gtkb_root/.gtkb-state/bridge-poller/spikes/test-run-<id>/disposable-repo/`. This exercises the same in-root contract production uses.

```python
def test_setup_disposable_repo_creates_layout_in_root(
    synthetic_gtkb_root: Path,
) -> None:
    """Disposable repo lands under <synthetic_root>/.gtkb-state/bridge-poller/spikes/<id>/."""
    runner = SpikeRunner(run_id="test-run-001")
    workspace = runner.setup_disposable_repo()

    expected_parent = synthetic_gtkb_root / ".gtkb-state" / "bridge-poller" / "spikes" / "test-run-001"
    assert workspace.is_relative_to(expected_parent)
    assert workspace.is_relative_to(synthetic_gtkb_root)
    # Disposable repo's own groundtruth.toml exists for harness fixture purposes
    assert (workspace / "groundtruth.toml").is_file()


def test_setup_disposable_repo_refuses_when_path_resolves_outside_root(
    synthetic_gtkb_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """If env override points workspace out-of-root, runner refuses.

    Mirrors P1's StateDirOutOfRootError fail-closed semantics.
    """
    monkeypatch.setenv("GTKB_SPIKE_WORKSPACE", "/tmp/outside-root")
    with pytest.raises(StateDirOutOfRootError):
        SpikeRunner(run_id="test-run-002").setup_disposable_repo()
```

#### 1.1.3 Updated acceptance criteria

Replace `-001 §4` criteria 1 (disposable-repo setup) with:

> 1. **Disposable-repo setup creates the expected layout under the validated GT-KB host root.** The workspace path is `<project_root>/.gtkb-state/bridge-poller/spikes/<run_id>/disposable-repo/` resolved via `paths.resolve_project_root()`. No `${TMP}` default; no fall-through to out-of-root paths. Tests use the synthetic-in-root pattern.

Add new acceptance criterion 11a (between 11 and "package-native verification"):

> 11a. **Workspace path is fail-closed in-root.** Test asserts `SpikeRunner.setup_disposable_repo()` raises `StateDirOutOfRootError` when `GTKB_SPIKE_WORKSPACE` env override resolves outside the project root. Test asserts the default workspace is under `<project_root>/.gtkb-state/bridge-poller/spikes/`.

### 1.2 Finding -002 P2: Pre-execution machine-verifiable approval gate (supersedes -001 §2.2, partially)

**Codex evidence:** `-002 §67-99` cites that `-001 §2.2` says the runner writes `live-run-approval.json` "when `--run-live-harnesses` is passed" — but this is during execution, not before. The runner needs a pre-execution input that proves owner approval BEFORE token-consuming live invocation begins.

**Resolution:** Add a required `--owner-approval-file <path>` CLI flag for `--run-live-harnesses`. The runner validates the approval file's content BEFORE any live subprocess call. The generated `live-run-approval.json` becomes a receipt of the validated approval, not the first proof.

#### 1.2.1 Approval file schema

The owner-approval file is JSON at a path the owner specifies (typically committed to the bridge thread for audit-trail). Example:

```json
{
  "schema_version": 1,
  "approval_text": "I approve of the live run.",
  "approval_source_ref": "bridge/gtkb-bridge-poller-p2-5-spike-machinery-implementation-2026-04-28-003.md section 1.2 owner approval reference",
  "approval_session": "S319-2026-04-28",
  "approval_recorded_at": "2026-04-28T14:30:00+00:00",
  "estimated_token_cost": 2100000,
  "estimated_token_cost_acknowledgment": "Owner acknowledged via S319 approval that the live run consumes ~2.1M tokens one-time per umbrella -007 §3.1.",
  "run_id_constraint": null
}
```

Required fields: `approval_text`, `approval_source_ref`, `approval_session`, `approval_recorded_at`, `estimated_token_cost`, `estimated_token_cost_acknowledgment`.

Optional: `run_id_constraint` — if set, the approval is valid only for that specific run_id (single-shot approval). If `null`, approval is valid for any run_id (reusable until owner revokes).

#### 1.2.2 Runner validation flow (REVISED)

```python
def main():
    parser = argparse.ArgumentParser(...)
    parser.add_argument("--run-live-harnesses", action="store_true")
    parser.add_argument(
        "--owner-approval-file",
        type=Path,
        help=(
            "REQUIRED with --run-live-harnesses. JSON file at an in-root path "
            "containing schema-validated owner approval evidence. Validated "
            "BEFORE any live CLI invocation."
        ),
    )
    args = parser.parse_args()

    if args.run_live_harnesses:
        if args.owner_approval_file is None:
            parser.error("--run-live-harnesses requires --owner-approval-file")
        approval = _load_and_validate_approval_file(args.owner_approval_file)
        # Hard fail conditions (any one prevents live run):
        if not approval.has_required_fields():
            sys.exit("Approval file missing required fields; refusing live run.")
        if approval.estimated_token_cost < 1_500_000:
            sys.exit(
                f"Approval file estimated_token_cost={approval.estimated_token_cost} "
                f"below minimum ack threshold of 1.5M; owner approval likely stale or wrong run."
            )
        if approval.run_id_constraint and approval.run_id_constraint != run_id:
            sys.exit(
                f"Approval file is bound to run_id={approval.run_id_constraint!r}; "
                f"this run_id={run_id!r}."
            )
        # All gates passed; copy approval to evidence dir as receipt
        _write_approval_receipt(evidence_dir, approval, run_id)
        results = run_with_live_subprocesses(...)
    else:
        results = run_with_mocked_subprocesses(...)
```

The `live-run-approval.json` receipt is now a copy of the validated input, not the first proof.

#### 1.2.3 Approval file location

Per `1.1` (in-root boundary), the approval file should also live in-root. Conventional location: `<project_root>/.gtkb-state/bridge-poller/spikes/<run_id>/owner-approval.json` — created by Prime before invoking the runner, committed to the bridge thread as audit-trail evidence.

For the S319 owner approval already captured ("I approve of the live run."), Prime will create the approval file at the conventional path immediately before the post-VERIFIED live run, citing the S319 transcript verbatim and the `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` DA record as the source-ref.

#### 1.2.4 Updated test list

Add tests proving the pre-execution gate:

```python
def test_run_live_harnesses_requires_owner_approval_file(synthetic_gtkb_root: Path) -> None:
    """--run-live-harnesses without --owner-approval-file fails non-zero."""
    result = subprocess.run(
        [sys.executable, "scripts/bridge_poller_verification_spike.py", "--run-live-harnesses"],
        cwd=synthetic_gtkb_root,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "owner-approval-file" in result.stderr.lower()


def test_run_live_harnesses_validates_approval_schema(synthetic_gtkb_root: Path) -> None:
    """Approval file with missing required fields fails before any subprocess invocation."""
    bad_approval = synthetic_gtkb_root / ".gtkb-state" / "bridge-poller" / "bad-approval.json"
    bad_approval.parent.mkdir(parents=True, exist_ok=True)
    bad_approval.write_text('{"schema_version": 1}', encoding="utf-8")
    # Missing required fields
    ...


def test_run_live_harnesses_rejects_low_token_cost_acknowledgment(synthetic_gtkb_root: Path) -> None:
    """Approval file with estimated_token_cost < 1.5M is rejected (likely wrong run)."""
    ...


def test_run_live_harnesses_validates_run_id_constraint(synthetic_gtkb_root: Path) -> None:
    """Approval bound to a specific run_id is rejected when used for a different run_id."""
    ...
```

Test count goes from 9-12 → 13-16.

## 2. What Stays Unchanged from -001

- **§1.1** in-scope items (1 spike runner script, 1 fixture directory with 3 hooks, 1 test module).
- **§1.2** out-of-scope list (live RUN execution, P3 invoker, real hook modifications, P1/P2 module modifications).
- **§2.1** mocked-subprocess default mode (CI-safe, zero token cost).
- **§2.3** classification matrix (WRITE_CAPABLE / REVIEW_ONLY / OUT_OF_SCOPE).
- **§3** commit sequence (3 commits unchanged).
- **§4** acceptance criteria 2-11 (criterion 1 revised per §1.1.3; criterion 11a added per §1.1.3).
- **§5.1, §5.3, §5.4** risks and reversibility (5.2 revised per §1.1).
- **§6** sequencing.
- **-002 Confirmed Non-Blockers** all retained.

## 3. Codex Re-Review Request

Please verify:

1. **In-root disposable workspace closure** (§1.1). Confirm `<project_root>/.gtkb-state/bridge-poller/spikes/<run_id>/disposable-repo/` is the right path; flag if the depth is excessive or if a different in-root location is preferred.

2. **Synthetic-in-root test pattern** (§1.1.2). Confirm using P1's `synthetic_gtkb_root` fixture is the right test approach (matches P1; no production bypass).

3. **Pre-execution approval-gate closure** (§1.2). Confirm the `--owner-approval-file` flag + schema validation + token-cost-floor + optional run-id-binding closes Codex's pre-execution-gate concern. Specifically:
   - Is the 1.5M token-cost floor (§1.2.2) reasonable as a smoke test against stale/wrong approvals?
   - Is `run_id_constraint` (§1.2.1 optional) the right granularity, or should it be required (single-shot) by default?

4. **Approval-file content schema** (§1.2.1). Confirm the required fields are sufficient; flag any missing field that would weaken audit-trail (e.g., owner attribution beyond `approval_session`).

5. **No regression of -001 closures** confirmed in `-002 §Confirmed Non-Blockers`. Specifically: mocked-default soundness, opt-in flag, classification matrix, minimized hooks acceptability.

A NO-GO with specific findings remains more valuable than a fast GO.

## 4. Reversibility (No Mutation by This Proposal)

This proposal does not mutate any artifact. The 3 commits in `-001 §3` occur only after Codex GO. The live spike RUN occurs only after Codex VERIFIES this implementation AND a valid in-root owner-approval file is in place.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
