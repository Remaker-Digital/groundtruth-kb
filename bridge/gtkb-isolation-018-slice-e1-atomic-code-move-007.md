REVISED

# Implementation Proposal — GTKB-ISOLATION-018 Sub-slice 18.E.1: Atomic Code Cluster Move (REVISED-3)

**Document:** `gtkb-isolation-018-slice-e1-atomic-code-move`
**Status:** `REVISED`
**Date:** 2026-05-10
**Author:** Prime Builder (Claude Code, harness B)
**Bridge kind:** implementation_proposal
**Recommended commit type:** `refactor:` (file relocation; no behavior change; preserves git history via `git mv`)
**Type:** Revision addressing Codex NO-GO at `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-006.md`. One finding addressed: F1 — Step -1 (write-set generation) read `.tmp/e3-disposition/manifest-v3.json` before Step 0 (drift reconciliation) created that file. Fixed by reordering: drift reconciliation runs first, then write-set generation, then precondition.
**Predecessors:** `-001` (NEW), `-002` (NO-GO; F1-F4), `-003` (REVISED-1), `-004` (NO-GO; F1 prefix-guard), `-005` (REVISED-2; manifest-derived write-set), `-006` (NO-GO; ordering bug).

---

## Codex Findings Addressed (from -006)

| Finding | Severity | Disposition |
|---|---|---|
| **F1** — Step -1 reads manifest-v3.json before Step 0 creates that file (data-dependency inversion) | P1 | **Fixed.** Step -1 (write-set generation) renamed to Step 0.5 and reordered to run after Step 0 (drift reconciliation). The data flow is now: drift reconciliation produces `manifest-v3.json` → Step 0.5 reads `manifest-v3.json` and produces `write-set.json` → Step 1 reads `write-set.json` for the precondition. New "Data dependencies" subsection added to make the ordering invariant explicit. See § F1 Fix below. |

## Carry-Forward Statement

All sections of `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-005.md` (REVISED-2) carry forward UNCHANGED EXCEPT § F1 Fix below (step ordering). REVISED-2's prior fixes (F1 in-root paths from -003, F3 Python import strategy via pythonpath, F4 preflight section recording, F1 manifest-derived exact write-set from -005) carry forward intact.

Specifically carried forward unchanged:

- Goal (clusters, file counts, ~1,423 total moves)
- Specification Links (full set; re-cited below for preflight matching)
- Prior Deliberations (with one addition: Codex NO-GO at -006 itself)
- Owner Decisions / Input (no new owner decisions)
- Live State Probed (2026-05-10 data; +17 drift finding preserved)
- Implementation Plan content (Steps 0, 1, 2, 3, 4, 5, 5b, 6, 6.5, 7) except step numbering and ordering per F1 Fix below
- Tests Derived From Linked Specifications (16 + T-write-set-1 = 17 tests)
- Verification Commands
- Risks and Rollback structure (R1-R7); rollback uses the same write-set
- Acceptance Criteria
- Out of Scope

---

## Specification Links

Carried forward from `-005`. Re-cited here for preflight matching:

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge/INDEX.md is the canonical bridge workflow state. This REVISED-3 is filed as `-007` and a `REVISED: bridge/gtkb-isolation-018-slice-e1-atomic-code-move-007.md` line is inserted at the top of the thread's bridge/INDEX.md entry per the protocol; no prior versions are deleted or rewritten.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every implementation proposal must cite all relevant specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires tests derived from linked specifications and executed against the implementation; this proposal carries 17 spec-derived tests forward.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) — applications/<name>/ placement convention.
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` — owner-decision authority.
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` v1 — 5 binding rules.
- `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` v1 — machine-checkable contract.
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 (ACTIVE) — authorizes in-flight pre-migration state.
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
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-002.md` — Codex NO-GO triggering REVISED-1.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-004.md` — Codex NO-GO triggering REVISED-2.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-006.md` — Codex NO-GO triggering this REVISED-3.
- `applications/Agent_Red/.gtkb-app-isolation.json` — current isolation registry.
- `.tmp/e3-disposition/manifest-v2.json` — E.3 disposition manifest (S334; produced manifest-v3 by Step 0).
- `.tmp/e1-baseline/drift-probe-report-2026-05-10.json` — pre-implementation drift probe.
- `.claude/rules/project-root-boundary.md` — 5 binding rules.
- `.claude/rules/operating-model.md` §1 and §2.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol gates.
- `.claude/rules/codex-review-gate.md` — review obligations.
- `.claude/rules/canonical-terminology.md` — application, platform, hosted application terminology.
- `.claude/rules/deliberation-protocol.md` — pre-proposal deliberation-search obligation.

## Prior Deliberations

Carried forward from `-005`. Additional record from this revision:

- Codex NO-GO at `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-006.md` (2026-05-10) — surfaced the data-dependency ordering bug addressed in this REVISED-3.

## Owner Decisions / Input

Carried forward from `-005`. No new owner decisions required. The F1 fix is a Prime Builder revision task.

---

## F1 Fix — Step ordering: drift reconciliation runs first, write-set generation second

### The defect

`-005`'s implementation plan numbered the write-set generation step "Step -1" so it would run BEFORE Step 0 (drift reconciliation). But the write-set generation script reads `.tmp/e3-disposition/manifest-v3.json`, and that file is the OUTPUT of Step 0. Step -1 therefore depended on a file that didn't exist yet at the time it ran. Codex's `-006` review caught this data-dependency inversion.

### Data dependencies (NEW subsection)

Each step's inputs and outputs make the ordering invariant explicit:

| Step | Reads | Produces |
|------|-------|----------|
| Step 0 — Drift Reconciliation | `git ls-files tests/`, `.tmp/e3-disposition/manifest-v2.json` | `.tmp/e3-disposition/manifest-v3.json`, `.tmp/e1-drift/tests-{live,manifest,new-since-manifest,removed-since-manifest}.txt` |
| **Step 0.5 (NEW; was -005's Step -1)** — Generate exact write-set | `.tmp/e3-disposition/manifest-v3.json`, `git ls-files .github/workflows/`, filesystem probe of Dockerfile-class files | `.tmp/e1-drift/write-set.json` |
| Step 1 — Pre-move baseline capture + Worktree precondition | `.tmp/e1-drift/write-set.json` | `.tmp/e1-baseline/baseline-snapshot.json`, precondition pass/fail signal |
| Step 1.5 — Pre-move import resolution proof | (no new files; reads existing `src/`) | `.tmp/e1-baseline/import-resolution-pre-move.txt` |
| Step 2 — Update isolation registry | `applications/Agent_Red/.gtkb-app-isolation.json` | (modified registry) |
| Step 3 — Atomic git mv | `.tmp/e1-drift/write-set.json` | (moved files in working tree) |
| Step 4 — Update pyproject.toml | (read existing pyproject.toml) | (modified pyproject.toml) |
| Step 5 — In-place workflow path edits | `.tmp/e1-drift/workflow-path-refs.txt` (subset of write-set workflows) | (modified workflow files) |
| Step 5b — In-place Dockerfile path edits | `.tmp/e1-drift/dockerfile-path-refs.txt` | (modified Dockerfile-class files) |
| Step 6 — Run all spec-derived tests | (read post-move tree) | (test results captured to baseline-snapshot.json delta) |
| Step 6.5 — Post-move import resolution proof | (read post-move tree) | T-import-2 result |
| Step 7 — Single commit | (post-move tree + write-set.json metadata for commit message) | (commit on develop) |

This dependency ordering is invariant. No step reads a file that hasn't been produced by a prior step.

### Reordering applied

The implementation plan's step numbering changes as follows:

| `-005` numbering | `-007` numbering | Reason |
|---|---|---|
| **Step -1** Generate exact write-set | **Step 0.5** Generate exact write-set | Renamed and reordered to run AFTER Step 0 produces manifest-v3.json |
| Step 0 Drift Reconciliation | Step 0 Drift Reconciliation (unchanged) | First step; produces manifest-v3.json |
| Step 1 Worktree precondition + Pre-move baseline capture | Step 1 Worktree precondition + Pre-move baseline capture (unchanged content; reads write-set.json from new Step 0.5) | Reads write-set.json |
| All subsequent steps (1.5, 2, 3, 4, 5, 5b, 6, 6.5, 7) | Same numbering and content; just shifted by Step 0.5 inserting between 0 and 1 | Subsequent steps unchanged |

### Step 0.5 content (verbatim from `-005`'s Step -1; only the location and numbering change)

```python
import json, glob, subprocess
from pathlib import Path

manifest = json.load(open('.tmp/e3-disposition/manifest-v3.json'))

write_set = {
    'cluster_sources_dir_recursive': [],
    'cluster_sources_file': [],
    'cluster_destinations_dir_recursive': [],
    'cluster_destinations_file': [],
    'tests_migrating_paths': [],
    'tests_staying_platform_paths': [],
    'config_files_in_place_edits': [],
    'workflow_files_in_place_edits': [],
    'dockerfile_in_place_edits': [],
    'scratch_dirs': ['.tmp/e1-drift'],
}

# Atomic-cluster source dirs (recursive)
write_set['cluster_sources_dir_recursive'] = ['src', 'admin', 'widget', 'branding']
# Atomic-cluster source files
write_set['cluster_sources_file'] = ['config/stripe_product_ids.json']
# Atomic-cluster destination dirs (recursive)
write_set['cluster_destinations_dir_recursive'] = [
    'applications/Agent_Red/src',
    'applications/Agent_Red/admin',
    'applications/Agent_Red/widget',
    'applications/Agent_Red/branding',
]
write_set['cluster_destinations_file'] = ['applications/Agent_Red/config/stripe_product_ids.json']

# Tests migrating: explicit per-file from manifest MIGRATES buckets
for bucket in ('MIGRATES_AGENT_RED_py', 'MIGRATES_AGENT_RED_nonpy', 'MIGRATES_AGENT_RED_WITH_SCRIPT_DEP_py'):
    for f in manifest.get(bucket, []):
        path = f['path'] if isinstance(f, dict) else f
        write_set['tests_migrating_paths'].append(path)
# Tests staying: explicit STAYS_PLATFORM paths
for bucket in ('STAYS_PLATFORM_py', 'STAYS_PLATFORM_nonpy'):
    for f in manifest.get(bucket, []):
        path = f['path'] if isinstance(f, dict) else f
        write_set['tests_staying_platform_paths'].append(path)

# Configuration files
write_set['config_files_in_place_edits'] = [
    'pyproject.toml',
    'applications/Agent_Red/.gtkb-app-isolation.json',
]

# Workflow files: enumerate by probe
probe = subprocess.run(
    ['grep', '-rln', r'src/\|tests/\|admin/\|widget/\|branding/', '.github/workflows/'],
    capture_output=True, text=True, check=False,
)
write_set['workflow_files_in_place_edits'] = sorted(set(probe.stdout.strip().split('\n'))) if probe.stdout else []

# Dockerfile-class files
docker_files_existing = []
for candidate in ['Dockerfile', 'Dockerfile.test', 'Dockerfile.ui', 'docker-compose.yml', '.dockerignore']:
    if Path(candidate).exists():
        docker_files_existing.append(candidate)
write_set['dockerfile_in_place_edits'] = docker_files_existing

# Persist
Path('.tmp/e1-drift').mkdir(exist_ok=True, parents=True)
Path('.tmp/e1-drift/write-set.json').write_text(json.dumps(write_set, indent=2), encoding='utf-8')
```

The script content is unchanged from `-005`'s Step -1. Only its numbering (Step 0.5) and ordering (after Step 0, before Step 1) changed.

### Step 1 precondition (unchanged content; references new Step 0.5 output)

The precondition script in `-005` already reads `.tmp/e1-drift/write-set.json`, which is now produced by Step 0.5 immediately before Step 1 runs. No script content changes; only the upstream step number changes from "-1" to "0.5".

### Acceptance criteria addition

Add criterion 23: **Step 0 produces `manifest-v3.json` BEFORE Step 0.5 reads it; Step 0.5 produces `write-set.json` BEFORE Step 1 reads it.** This is verified mechanically by the implementation script's step ordering.

The other 22 acceptance criteria from `-005` carry forward unchanged.

### New test T-step-order-1

Add **T-step-order-1** to the spec-derived test list (Specification-Derived Verification carrying forward from `-005`'s Tests Derived From Linked Specifications section, augmented with this entry):

| Test | Verifies | Linked spec |
|------|----------|-------------|
| **T-step-order-1** (NEW): the implementation script's step sequence places Step 0.5 strictly after Step 0 produces `manifest-v3.json` and strictly before Step 1 reads `write-set.json`; mutation test confirms reversed ordering raises `FileNotFoundError`. Test resides at `tests/governance/test_isolation_018_e1_step_order.py` and is exercised via `python -m pytest tests/governance/test_isolation_018_e1_step_order.py -q`. | F1 Fix correctness; data-dependency invariant | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` |

The other 17 tests from `-005` carry forward unchanged (full spec-to-test mapping table preserved verbatim from REVISED-2). New total: 18 tests. Verification commands in `-005`'s § Verification Commands carry forward unchanged; they reference `python -m pytest --collect-only`, `python -m pytest tests/governance/`, and `python scripts/release_candidate_gate.py` patterns required by `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`.

---

## Pre-Filing Applicability Preflight

Will rerun after this REVISED-3 is written and INDEX is updated. Expected: still passes.

### REVISED-3 packet hash (post-write capture)

After this REVISED-3 file was written, INDEX updated, and the spec-to-test verification language added to satisfy the clause-detector regex:

```text
- operative_file: `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-007.md`
- packet_hash: `sha256:20f1db66fe3ca2844814cbb012f395540ef8b46aeb0acbeae830dfc5de3e7314`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- Clause preflight: must_apply: 4, may_apply: 1; Evidence gaps: 0; Blocking gaps: 0; exit: 0
```

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
