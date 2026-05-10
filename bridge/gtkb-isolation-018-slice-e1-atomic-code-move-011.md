REVISED

# Implementation Proposal — GTKB-ISOLATION-018 Sub-slice 18.E.1: Atomic Code Cluster Move (REVISED-5)

**Document:** `gtkb-isolation-018-slice-e1-atomic-code-move`
**Status:** `REVISED`
**Date:** 2026-05-10
**Author:** Prime Builder (Claude Code, harness B)
**Bridge kind:** implementation_proposal
**Recommended commit type:** `refactor:` (file relocation; no behavior change; preserves git history via `git mv`)
**Type:** Revision addressing Codex NO-GO at `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-010.md`. One finding addressed: F1 — rollback `git restore --staged` + `git checkout --` sequence leaves destination-side files as untracked after `git mv`; destination cleanup is missing. Fixed with multi-phase rollback that explicitly removes destination-side untracked artifacts and an expanded T-write-set-1 that mechanically proves rollback completeness via a reproducible `git mv` + rollback + clean-status test.
**Predecessors:** `-001` NEW; `-002` NO-GO (4 findings); `-003` REVISED-1; `-004` NO-GO (prefix-guard); `-005` REVISED-2 (manifest-derived write-set); `-006` NO-GO (step ordering); `-007` REVISED-3 (Step 0 → 0.5 → 1); `-008` NO-GO (source-only test paths); `-009` REVISED-4 (symmetric source+destination test paths); `-010` NO-GO (rollback leaves destinations untracked).

---

## Codex Findings Addressed (from -010)

| Finding | Severity | Disposition |
|---|---|---|
| **F1** — Rollback sequence (`git restore --staged --` then `git checkout --`) unstages the destination-side `add` from `git mv` but leaves the destination file as untracked in the working tree; `git checkout --` cannot restore a path not in HEAD | P1 | **Fixed.** Replaced the single-pass rollback with a 4-phase algorithm: (Phase 1) reset index for all write-set paths; (Phase 2) restore sources from HEAD to recover original content at original locations; (Phase 3) explicitly remove destination-side untracked files and recursive directories created by `git mv`; (Phase 4) prune ephemeral parent directories created by the slice (e.g., `applications/Agent_Red/config/`). Containment: cleanup operates ONLY on paths in the generated write-set; never on paths outside the destination set. T-write-set-1 expanded with a mechanical reproducibility test: create a small temp git repo, run `git mv`, run the rollback helper, assert `git status --porcelain` returns clean. See § F1 Fix below. |

## Carry-Forward Statement

All sections of `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-009.md` (REVISED-4) carry forward UNCHANGED EXCEPT the F1 Fix below (rollback algorithm + T-write-set-1 expansion). REVISED-4's prior fix (symmetric source+destination test path tracking) carries forward intact.

Specifically carried forward unchanged:

- Goal (clusters, file counts, ~1,423 total moves)
- Specification Links (full set; re-cited below for preflight matching)
- Prior Deliberations (with one addition: Codex NO-GO at -010 itself)
- Owner Decisions / Input (no new owner decisions)
- Live State Probed (2026-05-10 data; +17 drift finding preserved)
- Implementation Plan content (Steps 0, 0.5, 1, 1.5, 2, 3, 4, 5, 5b, 6, 6.5, 7) — ordering and content from -009 preserved; only the rollback section's algorithm in § F1 Fix changes
- Tests Derived From Linked Specifications (T-write-set-1 expanded for rollback completeness; T-step-order-1 unchanged; T-import-2 unchanged; 15 from -001 unchanged)
- Verification Commands (carry forward; reference `python -m pytest`, `pytest`, `ruff`, `test_*.py` patterns required by clause detector)
- Risks and Rollback STRUCTURE (R1-R7); rollback ALGORITHM updated per F1 Fix
- Acceptance Criteria
- Out of Scope

---

## Specification Links

Carried forward from `-009`. Re-cited here for preflight matching:

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge/INDEX.md is the canonical bridge workflow state. This REVISED-5 is filed as `-011` and a `REVISED: bridge/gtkb-isolation-018-slice-e1-atomic-code-move-011.md` line is inserted at the top of the thread's bridge/INDEX.md entry per the protocol; no prior versions are deleted or rewritten.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every implementation proposal must cite all relevant specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires Specification-Derived Verification with spec-to-test mapping; this proposal carries 18 spec-derived tests (T-write-set-1 expanded for rollback completeness).
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
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-010.md` — Codex NO-GO triggering this REVISED-5.
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

Carried forward from `-009`. Additional record from this revision:

- Codex NO-GO at `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-010.md` (2026-05-10) — surfaced the rollback completeness defect addressed in this REVISED-5. Codex's review included a reproducible mini-experiment showing `git restore --staged` + `git checkout --` leaves the destination as untracked after `git mv`.

## Owner Decisions / Input

Carried forward from `-009`. No new owner decisions required. The F1 fix is a Prime Builder revision task per Codex `-010` line 178.

---

## F1 Fix — Multi-phase rollback that proves completeness

### The defect

Codex reproduced the issue with this minimal experiment:

```text
git mv tests/a.txt applications/Agent_Red/tests/a.txt
for p in tests/a.txt applications/Agent_Red/tests/a.txt:
    git restore --staged -- p
    git checkout -- p

status after proposed rollback sequence:
?? applications/
```

The destination `applications/Agent_Red/tests/a.txt` ends up as untracked. With ~1,423 file moves planned, the path-scoped rollback would leave hundreds of untracked destination files in the working tree on a partial-failure retry. That's exactly the kind of poisoned-state risk the path-scoped rollback was meant to prevent.

### Root cause

`git mv X Y` is, in index terms, `add Y; rm X` plus a rename in the working tree. Reversing requires:

1. Index reset for both X and Y: `git restore --staged -- X` and `git restore --staged -- Y`. After this, the index is clean (matches HEAD): X is in HEAD and present in the working tree; Y is not in HEAD and not in the index.
2. Working-tree restore for X: `git checkout -- X` — this fetches X's content from HEAD back to the working tree (X was deleted on disk by `git mv`).
3. Working-tree cleanup for Y: `git checkout -- Y` is invalid because Y isn't in HEAD. Y stays as untracked. **Explicit removal is required** — `Path(Y).unlink()` for files; `shutil.rmtree(Y)` for directories.
4. Parent-dir cleanup: directories created during `git mv` (e.g., `applications/Agent_Red/config/` if it didn't exist before) need to be pruned only if the slice created them and they're now empty.

### Replacement rollback algorithm — 4 phases, generated from the same write-set

Replace the rollback section with this multi-phase algorithm. The whole helper is scripted at `scripts/rollback_e1_write_set.py` (a new file added in this slice's implementation; details in the post-implementation report).

```python
import json, subprocess, shutil
from pathlib import Path

write_set = json.loads(Path('.tmp/e1-drift/write-set.json').read_text(encoding='utf-8'))

# ---------- Phase 1: reset index for ALL write-set paths ----------
all_index_paths = []
all_index_paths.extend(write_set['cluster_sources_dir_recursive'])
all_index_paths.extend(write_set['cluster_sources_file'])
all_index_paths.extend(write_set['cluster_destinations_dir_recursive'])
all_index_paths.extend(write_set['cluster_destinations_file'])
all_index_paths.extend(write_set['tests_migrating_source_paths'])
all_index_paths.extend(write_set['tests_migrating_destination_paths'])
all_index_paths.extend(write_set['config_files_in_place_edits'])
all_index_paths.extend(write_set['workflow_files_in_place_edits'])
all_index_paths.extend(write_set['dockerfile_in_place_edits'])

for p in all_index_paths:
    subprocess.run(['git', 'restore', '--staged', '--', p], check=False, capture_output=True)

# ---------- Phase 2: restore source-side and in-place-edited paths from HEAD ----------
sources_to_restore = []
sources_to_restore.extend(write_set['cluster_sources_dir_recursive'])
sources_to_restore.extend(write_set['cluster_sources_file'])
sources_to_restore.extend(write_set['tests_migrating_source_paths'])
# In-place-edited files are restored at their unchanged paths (source = destination)
sources_to_restore.extend(write_set['config_files_in_place_edits'])
sources_to_restore.extend(write_set['workflow_files_in_place_edits'])
sources_to_restore.extend(write_set['dockerfile_in_place_edits'])

for p in sources_to_restore:
    subprocess.run(['git', 'checkout', '--', p], check=False, capture_output=True)

# ---------- Phase 3: explicitly remove destination-side untracked artifacts ----------
destinations_to_clean = []
destinations_to_clean.extend(write_set['cluster_destinations_dir_recursive'])
destinations_to_clean.extend(write_set['cluster_destinations_file'])
destinations_to_clean.extend(write_set['tests_migrating_destination_paths'])

for p in destinations_to_clean:
    path = Path(p)
    if path.is_symlink() or path.is_file():
        path.unlink(missing_ok=True)
    elif path.is_dir():
        # Containment check: never operate outside applications/Agent_Red/ for destinations
        assert str(path).startswith('applications/Agent_Red/'), \
            f'Refusing to remove out-of-scope destination dir: {path}'
        shutil.rmtree(path, ignore_errors=True)

# ---------- Phase 4: prune ephemeral parent dirs created by the slice ----------
# applications/Agent_Red/config/ is the only NEW parent directory this slice creates;
# applications/Agent_Red/{src,admin,widget,branding,tests}/ have explicit destination entries above.
# After Phase 3 removes their contents, we prune empty parents bounded by the slice's destinations.
ephemeral_parents = ['applications/Agent_Red/config']

for p in ephemeral_parents:
    path = Path(p)
    if path.is_dir():
        try:
            path.rmdir()  # only succeeds if empty
        except OSError:
            pass  # not empty - leave it

print('Multi-phase rollback complete.')
```

**Containment**: every rollback operation is bounded by the write-set entries. Phase 3's destination cleanup includes an explicit assert that recursive directory removal never operates outside `applications/Agent_Red/`. Phase 4's ephemeral-parents list is a hard-coded short list (currently 1 entry), not derived from arbitrary disk scanning.

### Pre-commit Rollback Helper Location

Add `scripts/rollback_e1_write_set.py` (new file under GT-KB platform-script tooling) implementing the 4-phase algorithm. The helper is invoked manually after a partial Step 3 failure or via `make rollback-e1` if the project's Makefile is updated (Step 4 may add this convenience target).

The script's path is `scripts/rollback_e1_write_set.py` per platform-script convention; this is a NEW platform-tool file that lives under GT-KB-managed `scripts/` (Bucket-platform), not under `applications/Agent_Red/`. It is added in Step 1 (baseline + helper authoring), used in Step 6 if any test fails, and remains available for post-commit rollback verification per T-write-set-1.

### Post-commit Rollback (unchanged)

After Step 7 commit lands: `git revert <commit-sha>`. Single inverse-commit; clean.

### Risks R1-R3 update

R1, R2, R3 mitigations carry forward; their "Rollback:" lines now reference the 4-phase algorithm at `scripts/rollback_e1_write_set.py` and the same post-commit `git revert <sha>` path.

### T-write-set-1 (EXPANDED to prove rollback completeness)

The test now does end-to-end rollback verification:

| Test | Verifies | Linked spec |
|------|----------|-------------|
| **T-write-set-1** (UPDATED): the same `.tmp/e1-drift/write-set.json` content drives the precondition, rollback (4-phase algorithm), and Step 3 per-file `git mv` loop. **Rollback completeness**: a mechanical reproducibility test creates a temp git repo, places a small file at `tests/a.txt`, runs `git mv tests/a.txt applications/Agent_Red/tests/a.txt`, invokes `scripts/rollback_e1_write_set.py` with a synthetic write-set covering only this pair, and asserts `git status --porcelain` returns clean output (no `??` untracked entries, no staged changes, no working-tree changes vs HEAD). Mutation tests confirm: (1) omitting Phase 3 leaves the destination untracked and the test fails; (2) omitting Phase 2 leaves the source missing and the test fails; (3) Phase 3's containment assert fires when the synthetic write-set names a destination outside `applications/Agent_Red/`. Test resides at `tests/governance/test_isolation_018_e1_rollback_completeness.py`, exercised via `python -m pytest tests/governance/test_isolation_018_e1_rollback_completeness.py -q`. | F1 Fix correctness; rollback completeness; precondition-rollback-Step3 non-drift invariant; symmetric source-destination pairing; containment | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` |

T-step-order-1 from `-007` is unchanged. T-import-2 from `-003` is unchanged. The other 15 tests from `-001` carry forward unchanged. Total: 18 tests (T-write-set-1 expanded; T-step-order-1 added at -007; T-import-2 added at -003; 15 from -001).

### Acceptance criteria addition

- **Criterion 22 (REPLACES `-009`'s criterion 22):** The same `.tmp/e1-drift/write-set.json` is consumed by the precondition guard, the 4-phase rollback at `scripts/rollback_e1_write_set.py`, AND the Step 3 per-file `git mv` loop. T-write-set-1 verifies non-drift between all three consumers AND verifies rollback completeness via a mechanical reproducibility test (temp-repo `git mv` + 4-phase rollback + clean-status assertion).
- **Criterion 24 (NEW):** `scripts/rollback_e1_write_set.py` exists at the GT-KB-managed platform path, implements the 4-phase algorithm exactly as specified in § F1 Fix, and is exercised by T-write-set-1 (mutation tests confirm each phase is load-bearing for completeness).

The other 22 acceptance criteria from `-009` carry forward unchanged (criterion 23 from -007 about Step 0 → 0.5 → 1 ordering preserved).

---

## Out of Scope

Carried forward from `-009` unchanged. One additional explicit out-of-scope item:

- The new `scripts/rollback_e1_write_set.py` helper is specific to the E.1 write-set schema. Generalizing it to a reusable rollback-utility for other 18.x sub-slices is out of scope for this proposal; if 18.E.2 or later sub-slices want to reuse the algorithm, they file their own bridge proposal for the generalization.

## Pre-Filing Applicability Preflight

Will rerun after this REVISED-5 is written and INDEX is updated. Expected: still passes (only content changes are F1 fix; same spec citations, same content patterns; clause-detector regex satisfied via the spec-to-test verification language preserved from prior revisions).

### REVISED-5 packet hash (post-write capture)

After this REVISED-5 file was written and INDEX updated:

```text
- operative_file: `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-011.md`
- packet_hash: `sha256:e2f8d07c519cb7ddf1c9cafbf73157c8691e0681d6a8704f6ab9e12965918fa2`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- Clause preflight: must_apply: 4, may_apply: 1; Evidence gaps: 0; Blocking gaps: 0; exit: 0
```

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
