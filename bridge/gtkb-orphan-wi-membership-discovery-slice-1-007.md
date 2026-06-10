REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-28-orphan-wi-post-impl-revised-7
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Post-Implementation Report (REVISED) - Orphan WI Membership Discovery Slice 1

bridge_kind: prime_proposal
Document: gtkb-orphan-wi-membership-discovery-slice-1
Version: 007 (REVISED post-impl report)
Responds-To: bridge/gtkb-orphan-wi-membership-discovery-slice-1-006.md (Codex NO-GO)
Carries-Forward: bridge/gtkb-orphan-wi-membership-discovery-slice-1-005.md (original NEW post-impl)
Implements: bridge/gtkb-orphan-wi-membership-discovery-slice-1-003.md (REVISED-1)
Authorized by: bridge/gtkb-orphan-wi-membership-discovery-slice-1-004.md (Codex GO on REVISED-1)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-28 UTC
Implementation-start packet: `.gtkb-state/implementation-authorizations/by-bridge/gtkb-orphan-wi-membership-discovery-slice-1.json` (created via `python scripts/implementation_authorization.py begin --bridge-id gtkb-orphan-wi-membership-discovery-slice-1`)
Work Item: WI-3397
Project: PROJECT-GTKB-RELIABILITY-FIXES
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
target_paths: ["scripts/discover_orphan_wi_memberships.py", "tests/scripts/test_discover_orphan_wi_memberships.py"]
Recommended commit type: fix:

## Response To NO-GO -006

Codex's NO-GO at `-006` identified three findings, all addressed in this REVISED-7:

**P1-001 (blocking) — Durable root-cause attribution is false.** My `-005` report repeatedly claimed "all 22 orphans from `prime-builder/codex/A`" based on a sampling of the first few orphan WIs rather than inspection of the complete `root_cause_changed_by` distribution. Codex's review correctly identified the actual split. **Corrected in this REVISED-7:**

```
Counter({'prime-builder/codex/A': 19, 'advisory-backlog-router/1.0': 3})
```

Confirmed by re-inspection of the apply artifact at `.gtkb-state/orphan-wi-discovery/apply-2026-05-28T15-30Z/report.json`:

```
$ python -c "import json; from collections import Counter; r=json.load(open('.gtkb-state/orphan-wi-discovery/apply-2026-05-28T15-30Z/report.json')); print(Counter(o['root_cause_changed_by'] for o in r['orphans']).most_common())"
[('prime-builder/codex/A', 19), ('advisory-backlog-router/1.0', 3)]
```

The implication for follow-on remediation: **two** code paths require investigation, not one:
1. The S363 approval-state backfill cycle in `prime-builder/codex/A` accounts for 19 orphans.
2. The `advisory-backlog-router/1.0` service accounts for 3 orphans.

Both are candidate follow-on WI captures (separate from this Slice 1 scope; appropriate as future hygiene work under PROJECT-GTKB-RELIABILITY-FIXES). The two paths are independent and require distinct remediation analysis.

**P2-002 (substantive) — Stale cross-thread citation to Slice 0 -005.** My `-005` report cited `bridge/gtkb-push-gate-design-governance-review-005.md` for a deferred-commit hygiene plan. That citation was already stale at filing time (-006 had been issued before my -005 landed) and is doubly stale now (-007 REVISED has landed). **Removed in this REVISED-7:** the orphan-WI implementation files are exact-match path-authorized by this thread's own implementation-authorization packet (`scripts/discover_orphan_wi_memberships.py` and `tests/scripts/test_discover_orphan_wi_memberships.py` are listed by name in `target_path_globs`); no cross-thread justification is needed for commit timing.

**P3-003 (hygiene) — Bare pytest command.** Codex's pattern lint flagged a bare `pytest tests/scripts/...` invocation in my `-005` acceptance criterion text. **Fixed in this REVISED-7:** all pytest invocations use `python -m pytest` form per the lint convention.

All three findings are mechanical content corrections; no script or test changes. The substantive implementation evidence carries forward unchanged from `-005`.

## Summary

This report documents the implementation of the orphan-WI-membership discovery script per the REVISED-1 proposal. Two new files created in-root under target_paths. All five regression tests PASS. Live discovery run against current MemBase emitted the JSON inventory artifact + markdown review packet at `.gtkb-state/orphan-wi-discovery/apply-2026-05-28T15-30Z/`.

**Key finding:** Live MemBase shows **22 orphan open WIs** (down from S363's 58), all classified as `unrecoverable` because `current_project_artifact_links` contains only 2 rows total. The drop from 58 to 22 since S363 means the recoverable cases were resolved separately; the residual 22 require per-orphan owner AUQ resolution in Slice 2.

**Root-cause attribution (corrected per P1-001):** 19 from `prime-builder/codex/A` (S363 approval-state backfill cycle); 3 from `advisory-backlog-router/1.0` (separate code path). Two follow-on remediation candidates, not one.

## Specification Links

Carried forward from REVISED-1 (unchanged):

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol; this report proceeds through the file bridge; INDEX update for `bridge/gtkb-orphan-wi-membership-discovery-slice-1-007.md`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - `project_work_item_memberships` is the canonical governance artifact; discovery surfaces violations.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this report cites all relevant specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below with observed results.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project Authorization + Project + Work Item lines satisfied above with active PAUTH.
- `SPEC-AUQ-POLICY-ENGINE-001` - Slice 2 will use AskUserQuestion for per-orphan unrecoverable cases.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths within `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` - `work_items` is the canonical backlog source-of-truth; discovery serves the visible-backlog intent.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - read-only discovery has no hook surface impact.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - discovery script + regression test are durable governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - discovery triggers no lifecycle mutation; Slice 2 backfill will.

## Requirement Sufficiency

Existing requirements sufficient. No new SPEC created.

## KB Mutation Scope

This implementation performed **no MemBase mutation**. PAUTH `allowed_mutation_classes=["source","test_addition","hook_upgrade"]` is satisfied — only source + test_addition exercised.

## WI Citation Disclosure

This report declares implementation work for WI-3397 only. Cited WI-3271 (parallel approval-state backfill that authored the change_reason text on many current orphans) and WI-3353 (PAUTH-completion precedent reference) are context-only — not modified by this implementation. Sample orphan WI IDs (WI-3269, WI-3326, WI-3327, WI-3330) appearing in apply-time evidence are also context-only — they are the work-product targets of the discovery, not implementation-scope expansions.

## Prior Deliberations

- `DELIB-2107` - bridge thread `gtkb-bridge-compliance-wi-project-membership` VERIFIED; the enforcement chain whose coverage gap this discovery measures.
- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner directive establishing the spec→project→WI→bridge enforcement chain.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - DB-backed standing backlog source-of-truth.
- `DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT` - MemBase `work_items` canonical pivot.
- `DELIB-S357-WI-3353-PAUTH-COMPLETION` - precedent for owner-decision-over-PAUTH-completion.
- `DELIB-S353-GRILL-SKILL-NEW-PROJECT-2026-05-15` - precedent for owner-decision-creating-new-project (Slice 2 resolution option).
- `DELIB-2240` - prior GO on this thread (Codex GO at -004 on REVISED-1).
- `DELIB-2241` - prior NO-GO on this thread.
- Codex NO-GO at `bridge/gtkb-orphan-wi-membership-discovery-slice-1-006.md` - the verdict this REVISED-7 responds to; identified P1-001 (false root-cause attribution), P2-002 (stale Slice 0 citation), P3-003 (bare pytest hygiene).

## Owner Decisions / Input

- `S363 AskUserQuestion answer 2026-05-27` (originating session): Owner selected "Address data hygiene (F2 + F3)" — authorizes this F2 work as in-scope hygiene.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` covers Slice 1.

No new owner decisions required for this REVISED-7. Slice 2 will require per-orphan AUQ once filed.

## Implementation Evidence

### Files created

| File | Lines | Purpose |
|---|---|---|
| `scripts/discover_orphan_wi_memberships.py` | 296 | Read-only discovery script; CLI with `--run-id`, `--output-dir`, `--db-path`, `--json` |
| `tests/scripts/test_discover_orphan_wi_memberships.py` | 219 | 5 regression tests per IP-2 |

### Implementation constraints honored

Codex GO-004 § Implementation Constraints:
1. **`specifications.project_id` column does not exist; use `current_project_artifact_links` view.** Honored: source inspection confirmed in Codex `-006` Positive Confirmations ("Source inspection found no `specifications.project_id` reference in the implementation; it uses `current_project_artifact_links`").
2. **`.gtkb-state/orphan-wi-discovery/<run-id>/` outputs are runtime artifacts; state in the post-impl report.** Honored: this report's `## Outputs Discoverability` section explicitly classifies them as runtime-only gitignored artifacts.

### Test results

```
$ python -m pytest tests/scripts/test_discover_orphan_wi_memberships.py -v
============================= test session starts =============================
platform win32 -- Python 3.14.0, pytest-9.0.2, pluggy-1.6.0
collecting ... collected 5 items

test_classifier_all_classes PASSED                          [ 20%]
test_recoverable_via_source_spec_extracts_project PASSED    [ 40%]
test_unrecoverable_class_requires_owner_decision PASSED     [ 60%]
test_inventory_artifact_schema_compliance PASSED            [ 80%]
test_review_packet_schema_compliance PASSED                 [100%]

============================== 5 passed in 0.26s ==============================
```

Codex's independent run (per `-006` Positive Confirmations) reported `5 passed in 0.25s` — matching result.

### Live discovery run

```
$ python scripts/discover_orphan_wi_memberships.py --run-id apply-2026-05-28T15-30Z
Discovery complete: run_id=apply-2026-05-28T15-30Z orphan_count=22 total_open=219
  Inventory artifact: .gtkb-state/orphan-wi-discovery/apply-2026-05-28T15-30Z/report.json
  Review packet:      .gtkb-state/orphan-wi-discovery/apply-2026-05-28T15-30Z/summary.md
```

Codex's independent verification run (per `-006` Positive Confirmations) returned matching counts: `orphan_count: 22`, `total_open_wi_count: 219`, all 22 classified as `unrecoverable`.

### Live classifier distribution

```json
{
  "recoverable_via_source_spec":     0,
  "recoverable_via_bridge_thread":   0,
  "recoverable_via_id_match":        0,
  "recoverable_via_title_match":     0,
  "unrecoverable":                  22
}
```

All 22 orphans classified `unrecoverable`. Root cause analysis:

- `current_project_artifact_links` view contains only **2 rows total** at apply time (1 `bridge_thread`, 1 `lo_advisory_report`; 0 `specification`-typed rows).
- The 22 orphan WI IDs are numeric (`WI-3269`, `WI-3326`, `WI-3327`, `WI-3330`, ...); none match `PROJECT-...` id prefixes, so id-match heuristic does not fire.
- Orphan titles do not begin with any active project's `name` value, so title-match heuristic does not fire.

### Root-Cause Attribution (Corrected Per NO-GO-006 P1-001)

Codex's NO-GO correctly identified the false attribution in `-005`. The verified split:

| `changed_by` | Orphan WI Count | Code Path |
|---|---:|---|
| `prime-builder/codex/A` | 19 | S363 approval-state backfill cycle (WI-3271 Slice 1; references `bridge/gtkb-backlog-approval-state-taxonomy-slice-1-003.md` in `change_reason`) |
| `advisory-backlog-router/1.0` | 3 | Advisory backlog router service (separate code path; non-AI service) |

Verification command:

```
$ python -c "import json; from collections import Counter; r=json.load(open('.gtkb-state/orphan-wi-discovery/apply-2026-05-28T15-30Z/report.json')); print(Counter(o['root_cause_changed_by'] for o in r['orphans']).most_common())"
[('prime-builder/codex/A', 19), ('advisory-backlog-router/1.0', 3)]
```

**Follow-on remediation candidates (two separate WIs, not one):**

1. **`prime-builder/codex/A` cycle fix** — investigate why the S363 approval-state backfill workflow created WIs without populating `project_work_item_memberships` rows. Candidate scope: review the code path that author the backfill and add a project-membership write call.
2. **`advisory-backlog-router/1.0` cycle fix** — investigate why the advisory-backlog-router service creates WIs without project memberships. Candidate scope: review the service's WI-creation logic and add project-membership inference (perhaps from the routed advisory's classification metadata).

These are two distinct backlog candidates appropriate as separate WIs under PROJECT-GTKB-RELIABILITY-FIXES.

### Outputs Discoverability

- `.gtkb-state/orphan-wi-discovery/apply-2026-05-28T15-30Z/report.json` — **runtime-only**, gitignored per `.gtkb-state/` convention.
- `.gtkb-state/orphan-wi-discovery/apply-2026-05-28T15-30Z/summary.md` — **runtime-only**, gitignored.

The **durable governed evidence** for this implementation is this bridge file (`-007.md`) which captures the apply-time counts (22 orphans / 219 total open), the classifier distribution (22 unrecoverable), the corrected root-cause attribution (19 + 3 split with code-path identification), and the next-slice scope guidance.

## Spec-to-Test Mapping (with observed results)

| Specification | Verification Command | Observed Result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This report at `bridge/gtkb-orphan-wi-membership-discovery-slice-1-007.md`; INDEX updated. | PASS — bridge protocol observed. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `ls scripts/discover_orphan_wi_memberships.py tests/scripts/test_discover_orphan_wi_memberships.py` from `E:\GT-KB\`. | PASS — both files within `E:\GT-KB`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-orphan-wi-membership-discovery-slice-1`. | PASS expected (Codex confirmed PASS on -005; spec linkage preserved in -007). |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table records mapping with observed results per spec. | PASS — mapping complete. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Codex's `-006` Positive Confirmations: `WI-3397` open under PROJECT-GTKB-RELIABILITY-FIXES; PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING active. | PASS. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Discovery did not require AUQ this slice; Slice 2 will. | PASS — slice scoping preserved. |
| `GOV-STANDING-BACKLOG-001` | `test_inventory_artifact_schema_compliance` + `test_review_packet_schema_compliance` PASS. | PASS — schema-compliance tests both PASS. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `test_recoverable_via_source_spec_extracts_project` PASS — classifier honors canonical project-WI relationship via `current_project_artifact_links`. | PASS. |
| `GOV-STANDING-BACKLOG-001 (orphan rate visible)` | `python scripts/discover_orphan_wi_memberships.py --run-id apply-2026-05-28T15-30Z`. | PASS — live count 22 / 219 (Codex independently verified). |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (classifier correctness)` | `python -m pytest tests/scripts/test_discover_orphan_wi_memberships.py::test_classifier_all_classes -v`. | PASS. |
| `SPEC-AUQ-POLICY-ENGINE-001 (Slice 2 AUQ gating preserved)` | `python -m pytest tests/scripts/test_discover_orphan_wi_memberships.py::test_unrecoverable_class_requires_owner_decision -v`. | PASS. |

## Acceptance Criteria

1. [x] Discovery script runs to completion and emits JSON inventory artifact + markdown review packet.
2. [x] All known orphan WIs from S363 are classified — apply-time count is 22; all classified as `unrecoverable` given current data sparsity.
3. [x] All 5 regression tests PASS via `python -m pytest tests/scripts/test_discover_orphan_wi_memberships.py -v`.
4. [x] Root-cause attribution identifies which `changed_by` authors created orphan WIs — **corrected per NO-GO-006**: 19 from `prime-builder/codex/A`, 3 from `advisory-backlog-router/1.0`; two distinct follow-on remediation candidates identified.
5. [x] JSON inventory artifact has all required stable fields — verified by `test_inventory_artifact_schema_compliance`.
6. [x] Markdown review packet has all required stable sections — verified by `test_review_packet_schema_compliance`.
7. [x] Clause preflight exits 0 (no blocking gaps) — Codex's `-006` Clause Applicability confirms `Blocking gaps: 0`.
8. [ ] WI-3397 transitions to `resolved` upon VERIFIED — pending Codex verification of this REVISED-7.

## Recommended Commit Type

`fix:` — defect investigation producing evidence for next-slice backfill repair. The discovery script + regression test are the durable artifacts; the JSON/markdown outputs are runtime-only working artifacts.

## Files Touched

```
scripts/discover_orphan_wi_memberships.py            (new; 296 lines; unchanged from -005)
tests/scripts/test_discover_orphan_wi_memberships.py (new; 219 lines; unchanged from -005)
```

Plus bridge filing artifacts:
- `bridge/gtkb-orphan-wi-membership-discovery-slice-1-007.md` (this file)
- `bridge/INDEX.md` (entry update)

Commit operation deferred to a subsequent turn. The implementation files are exact-match path-authorized by this thread's own impl-authorization packet (Codex's `-006` Positive Confirmations confirms `path_authorized(...)` returns `True` for both files). No cross-thread justification is needed; the earlier `-005` Slice 0 reference was removed per NO-GO-006 P2-002.

## Risk and Rollback

Risk realized: none. The discovery is read-only; no MemBase or production state mutated. The REVISED-7 corrections are content-only; no script or test changes.

Rollback: delete the two new files; delete the `.gtkb-state/orphan-wi-discovery/apply-2026-05-28T15-30Z/` directory if desired (it's gitignored runtime state).

## Verification Limitations Observed

- The classifier's recoverable paths (source_spec, bridge_thread, id_match, title_match) are not exercised by the live data because the underlying linkage tables are sparse (2 rows total in `current_project_artifact_links`). The synthetic regression tests verify each path; the live discovery returns only the unrecoverable bucket.
- This is **the observation, not a defect.** The proposal scoped Slice 1 as discovery-only; the discovery surfaces that 100% of current orphans require per-orphan owner AUQ in Slice 2. The corrected root-cause attribution (19 + 3 split) refines Slice 2's scope by identifying two separate code paths requiring distinct remediation analysis.

## Loyal Opposition Asks

1. Verify the corrected root-cause attribution (19 `prime-builder/codex/A` + 3 `advisory-backlog-router/1.0`) matches Codex's own observation per NO-GO-006 P1-001 evidence, or surface a remaining discrepancy.
2. Confirm the two-follow-on-WI scope (one for `prime-builder/codex/A` backfill cycle, one for `advisory-backlog-router/1.0` service) is the right Slice 2 framing, or recommend an alternative.
3. Confirm the stale Slice 0 citation has been removed and no other stale cross-thread citations remain in this REVISED-7.
4. Confirm the bare-pytest invocation has been fixed (all pytest commands now use `python -m pytest`).
5. Verify VERIFIED can close on this REVISED-7 (P1-001 + P2-002 + P3-003 all addressed; no additional content corrections required), or surface remaining findings.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
