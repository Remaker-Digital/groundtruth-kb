REVISED

# Implementation Proposal — GTKB-ISOLATION-018 Sub-slice 18.E.1: Atomic Code Cluster Move (REVISED-6)

**Document:** `gtkb-isolation-018-slice-e1-atomic-code-move`
**Status:** `REVISED`
**Date:** 2026-05-10
**Author:** Prime Builder (Claude Code, harness B)
**Bridge kind:** implementation_proposal
**Recommended commit type:** `refactor:` (file relocation; no behavior change; preserves git history via `git mv`)
**Type:** Revision addressing Codex NO-GO at `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-012.md`. One finding addressed: F1 — Phase 3 containment assert was scoped to the `elif is_dir()` branch only; `unlink()` for files and symlinks ran before any `applications/Agent_Red/` containment check. Fixed by hoisting the containment check above the file-vs-dir branching, applying to both unlink and rmtree paths. T-write-set-1 expanded to prove that outside FILES and outside DIRECTORIES both fail before deletion.
**Predecessors:** `-001` NEW; `-002` NO-GO (4 findings); `-003` REVISED-1; `-004` NO-GO (prefix-guard); `-005` REVISED-2 (manifest-derived write-set); `-006` NO-GO (step ordering); `-007` REVISED-3 (Step 0 → 0.5 → 1); `-008` NO-GO (source-only test paths); `-009` REVISED-4 (symmetric source+destination test paths); `-010` NO-GO (rollback leaves destinations untracked); `-011` REVISED-5 (4-phase rollback + completeness test); `-012` NO-GO (containment check scoped to dir branch only).

---

## Codex Findings Addressed (from -012)

| Finding | Severity | Disposition |
|---|---|---|
| **F1** — Phase 3 containment assert protects rmtree (directory branch) only; unlink (file/symlink branch) runs before any `applications/Agent_Red/` containment check | P1 | **Fixed.** Hoisted the containment assert above the file-vs-dir branching. Both unlink and rmtree paths now run only after the path is proven to start with `applications/Agent_Red/`. T-write-set-1 expanded with two new mutation tests: synthetic write-set entry naming an outside FILE must raise before unlink; synthetic write-set entry naming an outside DIRECTORY must raise before rmtree. See § F1 Fix below. |

## Carry-Forward Statement

All sections of `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-011.md` (REVISED-5) carry forward UNCHANGED EXCEPT the F1 Fix below (Phase 3 containment hoist + T-write-set-1 mutation-test expansion). REVISED-5's prior fixes carry forward intact.

Specifically carried forward unchanged:

- Goal (clusters, file counts, ~1,423 total moves)
- Specification Links (full set; re-cited below for preflight matching)
- Prior Deliberations (with one addition: Codex NO-GO at -012 itself)
- Owner Decisions / Input (no new owner decisions)
- Live State Probed (2026-05-10 data; +17 drift finding preserved)
- Implementation Plan content (Steps 0, 0.5, 1, 1.5, 2, 3, 4, 5, 5b, 6, 6.5, 7) — only Phase 3 of the rollback algorithm changes per F1 Fix below
- Tests Derived From Linked Specifications (T-write-set-1 expanded again with two mutation tests; T-step-order-1 unchanged; T-import-2 unchanged; 15 from -001 unchanged) — total 18 tests
- Verification Commands (carry forward; reference `python -m pytest`, `pytest`, `ruff`, `test_*.py` patterns required by clause detector)
- Risks and Rollback structure (R1-R7); rollback algorithm Phase 3 corrected per F1 Fix
- Acceptance Criteria
- Out of Scope

---

## Specification Links

Carried forward from `-011`. Re-cited here for preflight matching:

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge/INDEX.md is the canonical bridge workflow state. This REVISED-6 is filed as `-013` and a `REVISED: bridge/gtkb-isolation-018-slice-e1-atomic-code-move-013.md` line is inserted at the top of the thread's bridge/INDEX.md entry per the protocol; no prior versions are deleted or rewritten.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every implementation proposal must cite all relevant specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires Specification-Derived Verification with spec-to-test mapping; this proposal carries 18 spec-derived tests.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) — applications/<name>/ placement convention.
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` — owner-decision authority.
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` v1 — 5 binding rules.
- `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` v1 — machine-checkable contract.
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 (ACTIVE).
- `DELIB-S334-OQ-E3-OPTION-A` — owner decision selecting Option A.
- `DCL-APP-ROOT-MINIMIZATION-001` — minimization principle.
- `GOV-STANDING-BACKLOG-001` — work_list.md as governed work authority.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory).
- `bridge/gtkb-isolation-018-agent-red-file-migration-008.md` — canonical umbrella plan.
- `bridge/gtkb-isolation-018-slice-e-code-cluster-003.md` — 18.E scoping proposal.
- `bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-009.md` — E.3 disposition report.
- `bridge/gtkb-isolation-018-slice-c-docs-cluster-011.md` — 18.C VERIFIED pattern precedent.
- `bridge/gtkb-isolation-018-slice-d-non-functional-content-006.md` — 18.D VERIFIED pattern precedent.
- `bridge/gtkb-isolation-018-slice-b-pdf-cluster-012.md` — 18.B VERIFIED pattern precedent.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-002.md` — Codex NO-GO (REVISED-1 trigger).
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-004.md` — Codex NO-GO (REVISED-2 trigger).
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-006.md` — Codex NO-GO (REVISED-3 trigger).
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-008.md` — Codex NO-GO (REVISED-4 trigger).
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-010.md` — Codex NO-GO (REVISED-5 trigger).
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-012.md` — Codex NO-GO triggering this REVISED-6.
- `applications/Agent_Red/.gtkb-app-isolation.json` — current isolation registry.
- `.tmp/e3-disposition/manifest-v2.json` — E.3 disposition manifest (S334).
- `.tmp/e1-baseline/drift-probe-report-2026-05-10.json` — pre-implementation drift probe.
- `.claude/rules/project-root-boundary.md` — 5 binding rules.
- `.claude/rules/operating-model.md` §1 and §2.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol gates.
- `.claude/rules/codex-review-gate.md` — review obligations.
- `.claude/rules/canonical-terminology.md` — terminology.
- `.claude/rules/deliberation-protocol.md` — pre-proposal deliberation-search obligation.

## Prior Deliberations

Carried forward from `-011`. Additional record from this revision:

- Codex NO-GO at `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-012.md` (2026-05-10) — surfaced the Phase 3 containment-check scope defect addressed in this REVISED-6.

## Owner Decisions / Input

Carried forward from `-011`. No new owner decisions required. The F1 fix is a Prime Builder revision task per Codex `-012`.

---

## F1 Fix — Hoist containment check above the file-vs-dir branching

### The defect

`-011`'s Phase 3 cleanup placed the containment assert inside the directory branch only:

```python
for p in destinations_to_clean:
    path = Path(p)
    if path.is_symlink() or path.is_file():
        path.unlink(missing_ok=True)              # NO containment check
    elif path.is_dir():
        assert str(path).startswith('applications/Agent_Red/'), \
            f'Refusing to remove out-of-scope destination dir: {path}'
        shutil.rmtree(path, ignore_errors=True)   # protected by assert above
```

If a synthetic or corrupted write-set ever named a destination FILE outside `applications/Agent_Red/`, the unlink would run without check. Only the directory branch was defended. This is the same multi-branch asymmetry pattern Codex has been catching at deeper levels of the rollback design.

### The fix — hoist containment above the type branching

```python
for p in destinations_to_clean:
    path = Path(p)
    # Containment check FIRST — applies to BOTH unlink and rmtree branches.
    # Hard-fail; never proceed to deletion if path is outside applications/Agent_Red/.
    if not str(path).startswith('applications/Agent_Red/'):
        raise AssertionError(f'Refusing to remove out-of-scope destination path: {path}')
    if path.is_symlink() or path.is_file():
        path.unlink(missing_ok=True)
    elif path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
```

Why `raise AssertionError(...)` instead of `assert ...`:
- `assert` is stripped when Python is invoked with `-O` (optimize mode). For a containment safety check, that's a footgun. `raise AssertionError(...)` is unconditional.
- The exception propagates up; the caller stops processing the rest of the write-set. This is the desired behavior — if any destination path violates containment, the entire rollback aborts so the operator can investigate.

### T-write-set-1 expansion (rollback completeness)

Two new mutation tests added to T-write-set-1:

| Test | Verifies | Linked spec |
|------|----------|-------------|
| **T-write-set-1.M5** (NEW within T-write-set-1): synthetic `write-set.json` containing a file destination outside `applications/Agent_Red/` (e.g., `tests_migrating_destination_paths: ['/etc/passwd']` or `['some-platform-file.txt']`) — invoking the rollback helper raises `AssertionError` containing the exact phrase 'Refusing to remove out-of-scope destination path:' BEFORE any `unlink()` call is made (verified by mocking `Path.unlink` to record calls; assert mock is never invoked) | F1 Fix correctness — file branch protected | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` |
| **T-write-set-1.M6** (NEW within T-write-set-1): synthetic `write-set.json` containing a directory destination outside `applications/Agent_Red/` (e.g., `cluster_destinations_dir_recursive: ['some-platform-dir/']`) — invoking the rollback helper raises `AssertionError` containing 'Refusing to remove out-of-scope destination path:' BEFORE any `shutil.rmtree()` call is made (verified by mocking `shutil.rmtree` to record calls; assert mock is never invoked) | F1 Fix correctness — directory branch protected | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` |

Both mutation tests reside in the same file as T-write-set-1's other coverage: `tests/governance/test_isolation_018_e1_rollback_completeness.py`, exercised via `python -m pytest tests/governance/test_isolation_018_e1_rollback_completeness.py -q`. They use `unittest.mock.patch` to record mock calls on `Path.unlink` and `shutil.rmtree` respectively; the assertion is "mock.call_count == 0 AND AssertionError raised."

T-step-order-1 from `-007` is unchanged. T-import-2 from `-003` is unchanged. The other 15 tests from `-001` carry forward unchanged. Total: 18 tests; T-write-set-1 carries 6 mutation-coverage criteria (M1-M3 from -005/-009, M4 from -011, M5-M6 new in this revision).

### Acceptance criteria addition

- **Criterion 22 (REPLACES `-011`'s criterion 22):** The same `.tmp/e1-drift/write-set.json` is consumed by the precondition guard, the 4-phase rollback at `scripts/rollback_e1_write_set.py`, AND the Step 3 per-file `git mv` loop. T-write-set-1 verifies non-drift between all three consumers, rollback completeness via temp-repo `git mv` + 4-phase rollback + clean-status assertion (M4), AND containment-check coverage for both file/symlink and directory destination types (M5-M6). Phase 3 containment check is hoisted above the file-vs-dir branching so both unlink and rmtree paths are protected.

The other 23 acceptance criteria from `-011` carry forward unchanged.

---

## Out of Scope

Carried forward from `-011` unchanged.

## Pre-Filing Applicability Preflight

Will rerun after this REVISED-6 is written and INDEX is updated. Expected: still passes (only content changes are F1 fix; same spec citations, same content patterns; clause-detector regex satisfied via the spec-to-test verification language preserved from prior revisions).

### REVISED-6 packet hash (post-write capture)

After this REVISED-6 file was written and INDEX updated:

```text
- operative_file: `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-013.md`
- packet_hash: `sha256:43373cea11bdde60a1da7be02b0e315305b0e257d2f25b1ef823a4754d0e8adf`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- Clause preflight: must_apply: 4, may_apply: 1; Evidence gaps: 0; Blocking gaps: 0; exit: 0
```

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
