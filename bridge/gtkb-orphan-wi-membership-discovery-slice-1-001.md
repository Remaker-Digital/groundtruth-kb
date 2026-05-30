NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-27-backlog-data-hygiene-f2-orphan-discovery
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Defect-Fix Proposal - Discover root cause and recoverability of 58 orphan open WIs lacking project membership (Slice 1: discovery only)

bridge_kind: implementation_proposal
Document: gtkb-orphan-wi-membership-discovery-slice-1
Version: 001 (NEW)
Date: 2026-05-27 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3397

target_paths: ["scripts/discover_orphan_wi_memberships.py", "tests/scripts/test_discover_orphan_wi_memberships.py"]

## Claim

58 of 191 open `work_items` (30%) have `project_name=null` AND no active row in `project_work_item_memberships`, despite the mechanical enforcement chain established by `gtkb-bridge-compliance-wi-project-membership` (DELIB-2107, VERIFIED). Many orphans are recent (`WI-3300`, `WI-3316`, `WI-3322`, `GTKB-AUTO-PUSH-INVESTIGATION-001`, etc.), indicating either a code path still creates orphans OR the enforcement landed after these specific creates OR the enforcement does not cover the path that created them. Sampled orphans show rich recoverable provenance (`source_spec_id`, bridge-thread references in `change_reason`). This proposal scopes Slice 1 as discovery-only: characterize the 58 orphans by recoverability class and emit a JSON report. Slice 2 (backfill + AUQ-per-orphan for unrecoverable items) is a planned follow-on whose scope depends on this discovery output.

## Defect / Reproduction

Live data state probe (S363 backlog review, 2026-05-27):

```
$ python -c "import json; b=json.load(open('C:/temp/backlog_open.json')); orphans=[wi for wi in b if not wi.get('project_name')]; print(f'orphan_count={len(orphans)}'); print(f'total_open_wi={len(b)}')"
orphan_count=58
total_open_wi=191

$ python -c "import json; b=json.load(open('C:/temp/backlog_open.json')); orphans=[wi for wi in b if not wi.get('project_name')]; from collections import Counter; print(Counter(wi.get('origin') for wi in orphans))"
Counter({'hygiene': 22, 'new': 16, 'defect': 14, 'improvement': 5, 'regression': 1})
```

Orphan WIs have priorities (only 3 of 58 lack one) so they were created with at least some metadata; the missing piece is consistently the project-linkage `project_name` field + the `project_work_item_memberships` row.

Sampled orphans:
- `WI-AUTO-SPEC-INTAKE-1262C1`: title "Implement SPEC-INTAKE-1262c1: grill-me-for-clarification owner clarification interview skill"; `source_spec_id='SPEC-INTAKE-1262c1'` (project recoverable via spec-id lookup)
- `WI-GTKB-GOV-CODE-QUALITY-BASELINE-SLICE-2`: title "GTKB-GOV-CODE-QUALITY-BASELINE Slice 2"; `change_reason` cites `bridge/gtkb-gov-code-quality-baseline-slice-2-007.md` (project recoverable via bridge-thread project linkage)
- `WI-3322`: title "spec-intake auto-WI IDs (WI-AUTO-*) are rejected by the bridge-compliance-gate" (recently created; recoverability unknown without further probe)

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`:
- `scripts/discover_orphan_wi_memberships.py`
- `tests/scripts/test_discover_orphan_wi_memberships.py`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; this proposal follows NEW/REVISED/GO/NO-GO/VERIFIED workflow
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - project_work_item_memberships is a canonical governance artifact; the orphan condition violates the canonical project-WI relationship
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant cross-cutting specs
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Specification-Derived Verification Plan maps acceptance criteria to specific test commands
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project Authorization + Project + Work Item header lines satisfied above with active PAUTH; this proposal's discovery directly serves this DCL's intent (every WI must have a project membership)
- `SPEC-AUQ-POLICY-ENGINE-001` - owner decision captured via AskUserQuestion (Owner Decisions section); future Slice 2 will use AUQ for per-orphan unrecoverable cases
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths within `E:\GT-KB`
- `GOV-STANDING-BACKLOG-001` - work_items is canonical backlog source-of-truth; orphan condition obscures project-level work selection
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - read-only discovery has no hook surface impact; parity preserved
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - creates two durable artifacts (discovery script + regression test); discovery report is itself a durable JSON artifact
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - discovery itself triggers no lifecycle mutation; Slice 2 backfill will

## Prior Deliberations

- `DELIB-2107` - bridge thread `gtkb-bridge-compliance-wi-project-membership` VERIFIED, 10 versions; established the enforcement chain that this proposal investigates for coverage gaps (why are orphans still being created after VERIFIED?)
- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner directive: spec to project to WI to bridge mechanical enforcement; this proposal surfaces gaps in that enforcement
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - owner directive formalizing standing backlog as DB-backed source-of-truth
- `DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT` - MemBase work_items is canonical backlog; orphan rows degrade canonical quality
- `DELIB-S357-WI-3353-PAUTH-COMPLETION` - precedent for owner-decision over project authorization completion (similar pattern for Slice 2 unrecoverable orphan AUQ pattern)
- `DELIB-S353-GRILL-SKILL-NEW-PROJECT-2026-05-15` - precedent for owner-decision creating a new dedicated project for an orphan-like WI (the unrecoverable-orphan resolution pattern for Slice 2)

## Owner Decisions / Input

- `S363 AskUserQuestion answer 2026-05-27`: Owner selected "Address data hygiene (F2 + F3)" in response to backlog prioritization+completeness report direction question. This answer authorizes F2 (this proposal) as in-scope hygiene work; recorded in this turn's transcript.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`: active standing project authorization covers F2 as reliability fast-lane data hygiene; verified via `gt projects authorizations PROJECT-GTKB-RELIABILITY-FIXES`.

## Requirement Sufficiency

Existing requirements sufficient. The canonical project-WI relationship is already mandated by `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` and enforced via bridge-compliance-gate. This proposal does not create a new requirement; it investigates an existing-rule violation surface and produces evidence to inform Slice 2 remediation scope. Slice 2 will not create new requirements either; it will apply backfill per existing constraints with owner AUQ for ambiguous cases.

## Proposed Scope

IP-1 - Discovery script

Add `scripts/discover_orphan_wi_memberships.py` with the following behavior:
- Query MemBase for all open work_items (`status` not in `{retired, resolved, verified, wont_fix, not_a_defect}`)
- For each WI, check `project_work_item_memberships` for an active row (`status='active' OR status IS NULL`)
- Classify orphan WIs by recoverability:
  - `recoverable_via_source_spec` - WI has `source_spec_id` set; spec is linked to a project via `project_artifact_links` or `specifications.project_id`
  - `recoverable_via_bridge_thread` - `change_reason` contains a bridge file path; bridge file's parent project can be derived
  - `recoverable_via_title_match` - WI title matches a `projects.name` prefix (e.g., "GTKB-FOO-BAR Slice 2" matches `PROJECT-GTKB-FOO-BAR`)
  - `recoverable_via_id_match` - WI ID prefix matches a project ID prefix (e.g., `WI-GTKB-GOV-CODE-QUALITY-BASELINE-SLICE-2` matches `PROJECT-GTKB-GOV-CODE-QUALITY-BASELINE`)
  - `unrecoverable` - none of the above heuristics yield a candidate project
- Emit JSON report to `.gtkb-state/orphan-wi-discovery/<run-id>/report.json` with per-WI classification, candidate project IDs (with confidence score 0-1.0), and root-cause attribution (which `changed_by` author created each orphan)
- Also emit a markdown summary `.gtkb-state/orphan-wi-discovery/<run-id>/summary.md` for human review
- Discovery is purely read-only; no DB writes

IP-2 - Regression test

`tests/scripts/test_discover_orphan_wi_memberships.py` adds three tests:
1. `test_classifier_all_classes` - table-driven test that the classifier produces the right class for each known recoverability pattern (against fixture WIs)
2. `test_recoverable_via_source_spec_extracts_project` - verifies the source-spec-to-project mapping logic
3. `test_unrecoverable_class_requires_owner_decision` - verifies that the unrecoverable class is preserved (not silently lumped with a low-confidence recoverable)

## Specification-Derived Verification Plan

| Spec citation | Verification artifact | Command | Expected outcome |
|---|---|---|---|
| GOV-STANDING-BACKLOG-001 (orphan rate visible) | Discovery script JSON report | python scripts/discover_orphan_wi_memberships.py --run-id manual-test | report.json includes orphan_count, orphan_count_by_class |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (classifier correctness) | test_classifier_all_classes | pytest tests/scripts/test_discover_orphan_wi_memberships.py::test_classifier_all_classes -v | PASS |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (canonical project-WI relationship) | test_recoverable_via_source_spec_extracts_project | pytest tests/scripts/test_discover_orphan_wi_memberships.py::test_recoverable_via_source_spec_extracts_project -v | PASS |
| SPEC-AUQ-POLICY-ENGINE-001 (Slice 2 AUQ gating preserved) | test_unrecoverable_class_requires_owner_decision | pytest tests/scripts/test_discover_orphan_wi_memberships.py::test_unrecoverable_class_requires_owner_decision -v | PASS |

## Acceptance Criteria

1. Discovery script runs to completion against live MemBase and emits JSON + markdown reports.
2. All 58 known orphan WIs from S363 are classified into one of the five recoverability classes.
3. All 3 regression tests PASS via `pytest tests/scripts/test_discover_orphan_wi_memberships.py -v`.
4. Root-cause attribution identifies which `changed_by` authors created orphan WIs (informs whether to file a follow-on WI to fix the originating code path).
5. WI-3397 transitions to `resolved` upon VERIFIED for Slice 1 (Slice 2 will be a separate WI + bridge thread).

## Risks / Rollback

- Risk: heuristic classifiers may misclassify some orphans (e.g., false-positive `recoverable_via_title_match`). Mitigation: per-WI confidence score (0-1.0) lets Slice 2 apply backfill only to high-confidence cases; lower-confidence cases get AUQ.
- Risk: discovery surfaces a large unrecoverable class that requires significant owner AUQ time in Slice 2. Mitigation: discovery output informs Slice 2 scoping; Slice 2 can batch AUQs or apply default-retire policy for sufficiently-old unrecoverable orphans with owner pre-approval.
- Risk: orphan count grows between Slice 1 and Slice 2. Mitigation: discovery is idempotent and can be re-run before Slice 2; root-cause attribution from Slice 1 may surface the originating code path for separate repair.
- Rollback: discovery is read-only; no rollback needed. Report files at `.gtkb-state/orphan-wi-discovery/` can be deleted if the discovery model is later revised.

## Files Expected To Change

- `scripts/discover_orphan_wi_memberships.py` (NEW)
- `tests/scripts/test_discover_orphan_wi_memberships.py` (NEW)

## Recommended Commit Type

`fix` - defect investigation; produces evidence for the next-slice backfill repair. The discovery script and its regression test are the durable artifacts.
