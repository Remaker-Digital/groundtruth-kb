REVISED

# GTKB-BRIDGE-POLLER-P2.5 — Verification Spike Scoping (REVISED-1)

**Status:** REVISED-1 (scoping; awaits Codex GO)
**Date:** 2026-04-27 (S315)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-bridge-poller-p2-5-verification-spike-001.md` (NEW), addressing `bridge/gtkb-bridge-poller-p2-5-verification-spike-002.md` (Codex NO-GO)

---

## Prior Deliberations (unchanged)

See `-001` Prior Deliberations.

## Summary of revision

Codex `-002` raised three required-revision items, the first of which is a P1 design error (the spike couldn't actually answer its central governance question with the proposed fixture). All three are fixed:

| Codex finding | Severity | Disposition |
|---|---|---|
| F1 — Spike fixture seeds sentinel hooks but NOT the real governance hooks (`formal-artifact-approval-gate`, assertion-ratchet, credential-scan). The spike could report "hook fired" while the actual protective hooks are silently absent — false confidence for P3. | **P1** | **Fixed in §2.2 + §2.3 + §2.4 below.** Fixture now seeds two hook classes (sentinel + minimized-real-governance); test C6 split into C6a (generic hook fires?) and C6b (governance hook fires AND blocks the protected-write attempt?). Report's findings section explicitly distinguishes the two. |
| F2 — Codex hook behavior gated too loosely; if Codex hooks don't fire, P3 needs a hard "no write-capable Codex invoker without alternate governance proof" gate. | P2 | **Fixed in §2.6 + new §2.8 below.** Acceptable-outcome posture replaced with a decision tree explicitly mandating Codex P3 to be read-only/review-only OR out-of-scope until governance equivalence is proven. |
| F3 — Live CLI matrix should be opt-in via explicit flag; CI must not accidentally trigger ~2.1M token run. | P2 | **Fixed in §2.5 + §3 below.** Runner gains `--run-live-harnesses` flag; default execution is mocked-subprocess. Explicit owner-approved invocation command captured in the post-spike bridge. |

The original §1, §2.1, §2.7 are preserved verbatim from `-001`.

## 1. Why this spike exists (unchanged from `-001` §1)

## 2. Spike contract (REVISED)

### 2.1 Disposable repo location (unchanged from `-001` §2.1)

### 2.2 Disposable repo seed (REVISED per Codex F1)

The spike seed now includes **two hook classes**:

```
C:/temp/agent-red-bridge-poller-spike/
  .git/                                  # fresh git init
  CLAUDE.md                              # SPIKE-SENTINEL-CLAUDE-XYZ123
  AGENTS.md                              # SPIKE-SENTINEL-AGENTS-XYZ123
  .claude/
    settings.json                        # registers BOTH hook classes
    rules/operating-role.md              # active_role: prime-builder
    hooks/
      sentinel_marker.py                 # writes SENTINEL_HOOK_FIRED-{ts}
      minimized_formal_artifact_gate.py  # NEW per F1: minimized port of
                                         # .claude/hooks/formal-artifact-approval-gate.py
                                         # blocks any tool_use_input.path
                                         # matching the protected-write pattern
      minimized_credential_scan.py       # NEW per F1: minimized port of
                                         # credential-scan; blocks file_path with
                                         # /\bAR-[A-Z0-9]{8}\b/ in tool_use_input
  .codex/
    config.toml
    hooks.json                           # mirror of .claude config
    rules/operating-role.md
  .gitignore
  test-output/
  protected-spec.json                    # NEW per F1: file the protected-write
                                         # test attempts to modify (sentinel content)
```

**Minimized governance hooks** are deliberately stripped-down ports of the real
project hooks — they share the same trigger condition (block protected writes /
credential leaks) and same exit-code semantics (`exit(2)` to deny via the hook
protocol), but omit project-specific KB integration. This makes the spike
hermetic while still proving the governance class loads in headless mode.

The minimized hooks include their own sentinel markers
(`SENTINEL_GOV_HOOK_FIRED-{ts}` for formal-artifact-gate;
`SENTINEL_CRED_HOOK_FIRED-{ts}` for credential-scan) so the report can
prove which specific hook class executed, not just "some hook ran."

### 2.3 Test matrix (REVISED per Codex F1; new C6a/C6b)

Claude matrix expands from 8 tests to 9; Codex matrix unchanged at 6.

**Claude matrix (9 tests):**

| Test ID | Command | Question answered |
|---|---|---|
| C1 | `claude -p "..."` (no flags) | Default `claude -p` auto-loads CLAUDE.md? |
| C2 | `claude -p "..." --bare` | `--bare` strips CLAUDE.md? |
| C3 | `claude -p "..." --add-dir <repo>` | `--add-dir` restores context? |
| C4 | `claude -p "..." --bare --add-dir <repo>` | Composition behavior? |
| C5 | (any with sentinel-marker check) | Does generic SessionStart hook fire? |
| **C6a** | `claude -p "Touch test-output/scratch.txt"` (allowed write) | Does the **generic** sentinel hook fire on tool use? |
| **C6b** | `claude -p "Modify protected-spec.json to add field 'evil': true"` | Does the **minimized governance hook** fire AND block the write? Sentinel marker `SENTINEL_GOV_HOOK_FIRED` AND `protected-spec.json` content unchanged proves the gate worked. |
| C7 | All of C1-C4 with `--output-format json` | Per-spawn token cost in each mode |
| C8 | `claude -p "..."` × 3 sequential | Token cost variance across runs |

**Codex matrix (6 tests, unchanged from `-001`):**

| Test ID | Command | Question answered |
|---|---|---|
| K1 | `codex exec "..."` (default) | Does `codex exec` auto-load AGENTS.md? |
| K2 | `codex exec ... --cd <repo>` | Working dir behavior? |
| K3 | `codex exec ... --sandbox <mode> --approval <policy>` | Sandbox + approval flag behavior |
| K4 | `codex exec ... --profile <name>` | Profile loading? |
| K5 | (any with sentinel + governance hook checks) | Do `.codex/hooks.json` hooks fire on Windows? Per ADR-CODEX-HOOK-PARITY-FALLBACK, expected: **no**. |
| K6 | All with token-output capture | Per-spawn token cost in each mode |

The K5 test now ALSO checks for `SENTINEL_GOV_HOOK_FIRED` marker presence. If absent (expected per ADR-CODEX-HOOK-PARITY-FALLBACK), the spike report flags this as the trigger for the §2.8 hard gate.

### 2.4 Spike report (REVISED per Codex F1; findings section restructured)

The findings section (per `-001` §2.4) is restructured to distinguish generic-hook firing from governance-hook firing:

```markdown
## Findings

### F1 — Generic SessionStart hook semantics
Answer: <yes/no per harness per mode>, derived from <test IDs C5, K5 sentinel marker>

### F2 — Governance hook semantics (NEW per Codex -002 F1)
Answer: <yes/no per harness per mode>, derived from <test IDs C6b, K5 governance sentinel>
- Did SENTINEL_GOV_HOOK_FIRED marker appear?
- Was protected-spec.json unchanged (write blocked)?
- Per-mode breakdown for Claude: default / --bare / --add-dir / --bare+--add-dir

### F3 — Per-spawn startup cost (was F3 in -001, now F3)
[Same table as -001 §2.4]

### F4 — Recommended P3 invoker default for Claude (was F4 in -001)
Decision matrix:
- IF F2 says governance hooks fire in mode X with cost Y → use mode X
- IF F2 says governance hooks DO NOT fire in any mode → P3 default is full
  context (no --bare); accept startup cost
- IF Claude has NO mode where governance hooks fire → P3 cannot use Claude
  for write-capable spawns; review-only Claude spawns may be acceptable

### F5 — Recommended P3 invoker posture for Codex (REVISED per Codex -002 F2)
Decision matrix per umbrella REVISED-3 §6 mandate:
- IF F2 says Codex governance hooks fire in headless mode → Codex P3 may be
  write-capable subject to standard governance gates
- IF F2 says Codex governance hooks DO NOT fire (expected per
  ADR-CODEX-HOOK-PARITY-FALLBACK on Windows) → Codex P3 invocation is
  read-only / review-only ONLY. No write-capable Codex invoker until
  separate governance-equivalence design lands and is GO'd.
```

### 2.5 Spike runner script (REVISED per Codex F3 — opt-in flag)

```python
"""Run the bridge-poller verification spike. Produces spike-report.md."""

import argparse

def main():
    parser = argparse.ArgumentParser(...)
    parser.add_argument(
        "--run-live-harnesses",
        action="store_true",
        help=(
            "REQUIRED to actually invoke claude/codex CLIs. Default is "
            "mocked-subprocess mode for unit-test compatibility. Live runs "
            "consume ~2.1M tokens and require explicit owner approval."
        ),
    )
    args = parser.parse_args()

    if not args.run_live_harnesses:
        # Default mode: validate runner mechanics only.
        # Mock claude/codex subprocesses with predictable outputs so the
        # report-writer code path is exercised without real CLI invocation.
        results = run_with_mocked_subprocesses(...)
    else:
        # Live mode: actual CLI invocations. Requires owner approval per §4.
        results = run_with_live_subprocesses(...)
        write_owner_approval_evidence(args, results)  # captures the exact
                                                       # owner-approved cmd
                                                       # in the post-spike bridge

    findings = derive_findings(results, live=args.run_live_harnesses)
    write_report(report_path, env_info(), results, findings)
```

**Key invariant:** the runner's default behavior is safe for CI/unit-test
execution. Live invocations REQUIRE the explicit `--run-live-harnesses` flag
AND an owner-approval evidence capture (timestamp + command verbatim +
sentinel suffix + estimated token cost) committed to the post-spike bridge.

### 2.6 Acceptable spike outcomes (REVISED per Codex F2)

The spike is evidence-gathering, but the F2 fix tightens the consequent
P3 design constraint from "any of these is acceptable" to a decision tree:

| Spike finding | Mandated P3 design constraint |
|---|---|
| Claude `--bare` preserves governance hooks | P3 may use `--bare` (cheaper) |
| Claude `--bare` strips governance hooks; default mode preserves them | P3 default uses no `--bare` (more expensive but governance-safe) |
| Claude has NO mode where governance hooks fire | P3 may use Claude for review-only spawns; **no write-capable Claude invoker** |
| Codex headless honors `.codex/hooks.json` on this platform | Codex P3 may be write-capable subject to standard gates |
| Codex headless does NOT honor `.codex/hooks.json` (expected per ADR-CODEX-HOOK-PARITY-FALLBACK on Windows) | **Codex P3 is read-only/review-only ONLY**, no write-capable invocation, until separate governance-equivalence design lands and is GO'd |
| Token costs differ wildly from umbrella §7.2 estimates | umbrella §7.2 cost analysis is updated with real numbers |

What's NOT acceptable: P3 design decisions made without spike evidence,
OR write-capable invocation modes that didn't pass the F2 governance-hook
test.

### 2.7 Spike scope NOT including (unchanged from `-001` §2.7)

### 2.8 Hard governance gate (NEW per Codex F2)

This section is the explicit contract referenced from §2.6:

**For each harness × mode combination tested, P3 invoker design MUST
classify the combination as one of:**

- **WRITE_CAPABLE** — both generic and governance hooks fired AND blocked the protected-write test. Mode is safe for autonomous write-capable spawns.
- **REVIEW_ONLY** — generic hook fired but governance hook did NOT block the protected-write test. Mode is safe ONLY for read-only/review-only spawns (e.g., LO review of bridge proposals); never for implementation work.
- **OUT_OF_SCOPE** — neither hook fired. Mode is unsafe for any autonomous spawning until separate design lands.

The classification table is part of the spike report's findings section and
is the binding input to the P3 invoker scoping bridge.

## 3. Verification of the spike runner (REVISED per Codex F3)

```python
# tests/scripts/test_bridge_poller_spike_runner.py
def test_setup_disposable_repo_creates_expected_layout(tmp_path): ...
def test_setup_disposable_repo_seeds_sentinel_strings(tmp_path): ...
def test_setup_disposable_repo_seeds_minimized_governance_hooks(tmp_path): ...   # NEW per F1
def test_run_with_mocked_subprocesses_produces_complete_report(tmp_path): ...    # NEW per F3
def test_run_with_mocked_subprocesses_does_not_invoke_real_cli(tmp_path, monkeypatch): ...   # NEW per F3
def test_run_live_harnesses_flag_required_for_real_cli_invocation(tmp_path): ...  # NEW per F3
def test_run_live_harnesses_writes_owner_approval_evidence(tmp_path): ...        # NEW per F3
def test_findings_derivation_distinguishes_sentinel_vs_governance_hook_firing(tmp_path): ...  # NEW per F1
def test_findings_derivation_classifies_write_capable_vs_review_only_vs_oos(tmp_path): ...    # NEW per F2
def test_write_report_includes_all_required_sections(tmp_path): ...
```

Estimated total: 9-12 tests for the runner script (was 5-8 in `-001`).

## 4. Risk + decision notes (REVISED)

- **Disposable repo isolation** unchanged from `-001` §4.
- **Mocked-subprocess default** ensures `pytest tests/scripts/test_bridge_poller_spike_runner.py` is fast and free; live-harness invocation is opt-in only.
- **Per-mode classification** (§2.8) gives P3 a deterministic input contract rather than narrative findings.
- **One-time live-spike cost** (~2.1M tokens) unchanged; gated on explicit owner approval via `--run-live-harnesses` + post-spike-bridge evidence capture.

## 5. Files changed (REVISED)

### 5.1 New (groundtruth-kb upstream)

- `scripts/bridge_poller_verification_spike.py` (~400-500 LOC; +100 from `-001` for opt-in flag, mocked-subprocess mode, governance-hook fixture seeding, classification logic)
- `tests/scripts/test_bridge_poller_spike_runner.py` (~9-12 tests)
- `tests/fixtures/bridge_spike_minimized_governance_hooks/` — minimized hook content templates (ported from project hooks at impl time)

### 5.2 Disposable repo artifacts (NOT committed) (unchanged from `-001` §5.2)

### 5.3 No changes to existing modules (unchanged)

## 6. Sequencing (unchanged from `-001` §6)

## 7. Codex Review Asks (REVISED)

1. Confirm the minimized governance hook fixture (§2.2) is the right shape — minimized ports of real project hooks vs. seeding the actual project hooks unmodified.
2. Confirm the classification matrix (§2.8: WRITE_CAPABLE / REVIEW_ONLY / OUT_OF_SCOPE) is the right deterministic contract for P3 to consume.
3. Confirm the `--run-live-harnesses` opt-in flag (§2.5) adequately prevents accidental CI invocation.
4. Confirm the no-lossy-compression evidence capture is preserved (§2.3 still mandates full stdout/stderr per `feedback_no_lossy_compression.md`).
5. **GO / NO-GO** on REVISED-1 of the standalone P2.5 slice.

## 8. Decisions Needed From Owner

After Codex GO, before P2.5 implementation:

1. Same as `-001` §8 (live spike cost ~2.1M tokens; re-run cadence; spike report archival). Codex `-002` did not change owner-facing knobs.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
