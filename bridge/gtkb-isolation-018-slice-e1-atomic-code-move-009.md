REVISED

# Implementation Proposal — GTKB-ISOLATION-018 Sub-slice 18.E.1: Atomic Code Cluster Move (REVISED-4)

**Document:** `gtkb-isolation-018-slice-e1-atomic-code-move`
**Status:** `REVISED`
**Date:** 2026-05-10
**Author:** Prime Builder (Claude Code, harness B)
**Bridge kind:** implementation_proposal
**Recommended commit type:** `refactor:` (file relocation; no behavior change; preserves git history via `git mv`)
**Type:** Revision addressing Codex NO-GO at `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-008.md`. One finding addressed: F1 — write-set omits destination paths for per-file migrated tests; precondition/rollback/T-write-set-1 consume only source paths. Fixed by making test-move tracking symmetrical: source AND destination paths both recorded, both consumed.
**Predecessors:** `-001` NEW; `-002` NO-GO (4 findings); `-003` REVISED-1; `-004` NO-GO (prefix-guard scope); `-005` REVISED-2 (manifest-derived write-set); `-006` NO-GO (step ordering); `-007` REVISED-3 (Step 0 → 0.5 → 1 ordering); `-008` NO-GO (test destinations missing).

---

## Codex Findings Addressed (from -008)

| Finding | Severity | Disposition |
|---|---|---|
| **F1** — Write-set omits destination paths for per-file migrated tests; precondition / rollback / T-write-set-1 consume source paths only | P1 | **Fixed.** Renamed `tests_migrating_paths` → `tests_migrating_source_paths`. Added new field `tests_migrating_destination_paths`. Step 0.5 generator computes both (`dest = "applications/Agent_Red/" + path` for each manifest row). Step 1 precondition consumes both. Rollback consumes both. T-write-set-1 verifies symmetric coverage. See § F1 Fix below. |

## Carry-Forward Statement

All sections of `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-007.md` (REVISED-3) carry forward UNCHANGED EXCEPT the F1 Fix below (write-set schema + precondition + rollback + T-write-set-1 update). REVISED-3's prior fix (Step 0 → 0.5 → 1 ordering) carries forward intact.

Specifically carried forward unchanged:

- Goal (clusters, file counts, ~1,423 total moves)
- Specification Links (full set; re-cited below for preflight matching)
- Prior Deliberations (with one addition: Codex NO-GO at -008 itself)
- Owner Decisions / Input (no new owner decisions)
- Live State Probed (2026-05-10 data; +17 drift finding preserved)
- Implementation Plan content (Steps 0, 0.5, 1, 1.5, 2, 3, 4, 5, 5b, 6, 6.5, 7) — ordering from -007 preserved; only Step 0.5 generator and Step 1 precondition + rollback CONTENT update per F1 Fix below
- Tests Derived From Linked Specifications (T-write-set-1 schema-coverage criterion expands to include destination-path symmetry; T-step-order-1 unchanged)
- Verification Commands (carry forward; reference `python -m pytest`, `pytest`, `ruff`, `test_*.py` patterns required by clause detector)
- Risks and Rollback structure (R1-R7); rollback consumes the symmetric write-set
- Acceptance Criteria
- Out of Scope

---

## Specification Links

Carried forward from `-007`. Re-cited here for preflight matching:

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge/INDEX.md is the canonical bridge workflow state. This REVISED-4 is filed as `-009` and a `REVISED: bridge/gtkb-isolation-018-slice-e1-atomic-code-move-009.md` line is inserted at the top of the thread's bridge/INDEX.md entry per the protocol; no prior versions are deleted or rewritten.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every implementation proposal must cite all relevant specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires Specification-Derived Verification with spec-to-test mapping; this proposal carries 18 spec-derived tests (T-write-set-1 expanded for symmetry).
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
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-008.md` — Codex NO-GO triggering this REVISED-4.
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

Carried forward from `-007`. Additional record from this revision:

- Codex NO-GO at `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-008.md` (2026-05-10) — surfaced the asymmetric source-only test write-set defect addressed in this REVISED-4.

## Owner Decisions / Input

Carried forward from `-007`. No new owner decisions required. The F1 fix is a Prime Builder revision task per Codex `-008` line 158.

---

## F1 Fix — Symmetric source + destination paths for per-file migrated tests

### The defect

`-007`'s write-set schema (carried forward from `-005`) has `tests_migrating_paths` enumerating only the source side of each per-file test move:

```python
for bucket in ('MIGRATES_AGENT_RED_py', 'MIGRATES_AGENT_RED_nonpy', 'MIGRATES_AGENT_RED_WITH_SCRIPT_DEP_py'):
    for f in manifest.get(bucket, []):
        path = f['path'] if isinstance(f, dict) else f
        write_set['tests_migrating_paths'].append(path)
```

The write-set therefore records `tests/multi_tenant/test_X.py` but not `applications/Agent_Red/tests/multi_tenant/test_X.py`. Step 1 precondition and the rollback path list both consume only `tests_migrating_paths`, so the destination side is invisible to:

1. The clean-or-scoped-worktree precondition: a partially-staged retry could leave files at the destination side that the precondition doesn't recognize, classifying them as out-of-scope on retry.
2. The path-scoped rollback: rolling back only source paths leaves destination-side files un-recovered after a partial failure between Step 3 sub-step 2 (per-file `git mv`) and Step 7 (commit).
3. T-write-set-1 (non-drift between precondition and rollback): symmetry is verified for source paths only.

The same defect does not exist for the recursive-cluster moves (`src/`, `admin/`, `widget/`, `branding/`, `config/`) because those have explicit `cluster_destinations_dir_recursive` and `cluster_destinations_file` fields. Tests are the only per-file move set, and the destination side was overlooked.

### Step 0.5 generator (UPDATED)

Replace the schema with:

```python
write_set = {
    'cluster_sources_dir_recursive': [],
    'cluster_sources_file': [],
    'cluster_destinations_dir_recursive': [],
    'cluster_destinations_file': [],
    'tests_migrating_source_paths': [],         # RENAMED from tests_migrating_paths
    'tests_migrating_destination_paths': [],    # NEW
    'tests_staying_platform_paths': [],
    'config_files_in_place_edits': [],
    'workflow_files_in_place_edits': [],
    'dockerfile_in_place_edits': [],
    'scratch_dirs': ['.tmp/e1-drift'],
}
```

The cluster-source / cluster-destination / config / workflow / dockerfile / scratch entries are unchanged from `-007`.

The tests-migrating loop becomes:

```python
for bucket in ('MIGRATES_AGENT_RED_py', 'MIGRATES_AGENT_RED_nonpy', 'MIGRATES_AGENT_RED_WITH_SCRIPT_DEP_py'):
    for f in manifest.get(bucket, []):
        source = f['path'] if isinstance(f, dict) else f
        destination = 'applications/Agent_Red/' + source
        write_set['tests_migrating_source_paths'].append(source)
        write_set['tests_migrating_destination_paths'].append(destination)
```

The tests-staying loop is unchanged.

A loop invariant assertion is added immediately after the tests-migrating loop:

```python
assert len(write_set['tests_migrating_source_paths']) == len(write_set['tests_migrating_destination_paths']), \
    'Source and destination paths must be paired one-to-one'
for src, dst in zip(write_set['tests_migrating_source_paths'], write_set['tests_migrating_destination_paths']):
    assert dst == 'applications/Agent_Red/' + src, f'Pair mismatch: {src} → {dst}'
```

### Step 1 precondition (UPDATED to consume both)

Replace the line that adds `write_set['tests_migrating_paths']` to `exact_paths` with:

```python
exact_paths.update(write_set['tests_migrating_source_paths'])
exact_paths.update(write_set['tests_migrating_destination_paths'])
```

The forbidden_paths set (STAYS_PLATFORM tests) is unchanged. The `acceptable_prefixes` list is unchanged.

### Pre-commit Rollback (UPDATED to consume both)

Replace the rollback list-building section that adds `write_set['tests_migrating_paths']` with:

```python
rollback_paths.extend(write_set['tests_migrating_source_paths'])
rollback_paths.extend(write_set['tests_migrating_destination_paths'])
```

The other rollback path categories are unchanged.

### Symmetric pairing in implementation Step 3

Step 3 sub-step 2 (per-file `git mv`) was already pair-driven in earlier revisions. Make the data source explicit:

```python
for src, dst in zip(write_set['tests_migrating_source_paths'], write_set['tests_migrating_destination_paths']):
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['git', 'mv', src, dst], check=True)
```

### T-write-set-1 (EXPANDED)

The test now verifies symmetric coverage:

| Test | Verifies | Linked spec |
|------|----------|-------------|
| **T-write-set-1** (UPDATED): the same `.tmp/e1-drift/write-set.json` content drives the precondition, rollback, and Step 3 per-file `git mv` loop. **Source-and-destination symmetry**: for every entry `S` in `tests_migrating_source_paths`, the corresponding entry `applications/Agent_Red/` + `S` exists at the same index in `tests_migrating_destination_paths`. Mutation tests confirm: (1) omitting `tests_migrating_destination_paths` from precondition fails the test; (2) omitting it from rollback fails; (3) reordering source/destination indices fails the pair-equality check. Test resides at `tests/governance/test_isolation_018_e1_write_set_symmetry.py`, exercised via `python -m pytest tests/governance/test_isolation_018_e1_write_set_symmetry.py -q`. | F1 Fix correctness; precondition-rollback-Step3 non-drift invariant; symmetric source-destination pairing | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` |

T-step-order-1 from `-007` is unchanged. The other 17 tests from `-005` carry forward unchanged. Total: 18 tests (T-write-set-1 expanded; T-step-order-1 added at -007; T-import-2 added at -003; 15 from -001).

### Acceptance criteria addition

- **Criterion 22 (REPLACES `-005`'s criterion 22):** The same `.tmp/e1-drift/write-set.json` is consumed by the precondition guard, the path-scoped rollback, AND the Step 3 per-file `git mv` loop. T-write-set-1 verifies non-drift between all three consumers. **Source-destination symmetry**: every entry in `tests_migrating_source_paths` has a corresponding entry at the same index in `tests_migrating_destination_paths` of the form `"applications/Agent_Red/" + source`.

The other 22 acceptance criteria from `-007` carry forward unchanged.

---

## Out of Scope

Carried forward from `-007` unchanged.

## Pre-Filing Applicability Preflight

Will rerun after this REVISED-4 is written and INDEX is updated. Expected: still passes (only content changes are F1 fix; same spec citations, same content patterns; clause-detector regex satisfied via the spec-to-test verification language preserved from `-007`).

### REVISED-4 packet hash (post-write capture)

After this REVISED-4 file was written and INDEX updated:

```text
- operative_file: `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-009.md`
- packet_hash: `sha256:7808eb337a01a3df1cfd7599e215a9d4e486ee1f310e08630501a46d275ab122`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- Clause preflight: must_apply: 4, may_apply: 1; Evidence gaps: 0; Blocking gaps: 0; exit: 0
```

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
