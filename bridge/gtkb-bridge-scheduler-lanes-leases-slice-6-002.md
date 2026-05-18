GO

# Loyal Opposition Review - Bridge Scheduler Slice 6: Aging and Priority Weighting

bridge_kind: review_verdict
Document: gtkb-bridge-scheduler-lanes-leases-slice-6
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-05-18 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-bridge-scheduler-lanes-leases-slice-6-001.md
Recommended commit type: feat:

## Verdict

GO for Slice 6 implementation.

This verdict approves the additive dispatch-priority scoring primitive described in `bridge/gtkb-bridge-scheduler-lanes-leases-slice-6-001.md`: a standalone `scripts/bridge_dispatch_priority.py` module plus focused tests in `platform_tests/scripts/test_bridge_dispatch_priority.py`.

The approved scoring shape is linear effective age: priority head-start hours plus `aging_rate * age_hours`. That satisfies the scoping decision that aging weight be monotonic increasing in `(now - filed_at)` and gives the intended bounded-over-fresh-work anti-starvation behavior. `DEFAULT_PRIORITY = "P3"` is acceptable for unprioritized bridge entries because it avoids treating omitted priority as either emergency work or bottom-of-queue work.

This GO does not authorize wiring the scorer into `scripts/cross_harness_bridge_trigger.py`, `scripts/single_harness_bridge_dispatcher.py`, or any live dispatch selector. Integration remains a later scheduler proposal/reporting step that must consume the Slice 2 lease registry, Slice 3 serialized INDEX writer, Slice 4 concurrency module, the corrected Slice 5 lane classifier, and this Slice 6 priority scorer together.

## Prior Deliberations

Deliberation Archive searches were run before review:

- `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config E:\GT-KB\groundtruth.toml deliberations search "gtkb-bridge-scheduler-lanes-leases-slice-6 aging priority weighting DELIB-2182 bridge scheduler" --limit 8 --json` returned `[]`.
- `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config E:\GT-KB\groundtruth.toml deliberations search "aging priority weighting old items starve fresh bridge noise S350" --limit 8 --json` returned `[]`.
- `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config E:\GT-KB\groundtruth.toml deliberations get DELIB-2182` retrieved the controlling owner authorization.

Relevant decision and bridge history:

- `DELIB-2182` records the owner's 2026-05-18 authorization for the full bridge scheduler program, including Slice 6 as aging and priority weighting.
- `bridge/gtkb-bridge-scheduler-lanes-leases-slice-1-scoping-002.md` is the GO verdict approving the five-slice scheduler plan and requiring follow-on implementation slices to restate concrete test coverage.
- `bridge/gtkb-bridge-scheduler-lanes-leases-slice-1-scoping-001.md` defines Slice 6 as "Item age (NEW/REVISED filed timestamp) and a priority field ... feed into the dispatch selector so old items don't starve" and design decision 5 as "Aging weight = monotonic increasing as a function of (now - filed_at)."
- `bridge/gtkb-bridge-scheduler-lanes-leases-slice-5-002.md` is the current NO-GO on the sibling lane-classifier primitive. Slice 6 may proceed as a standalone scoring primitive, but live scheduler integration must not proceed until the lane-classifier gap is corrected or explicitly handled in an integration proposal.

## Review Findings

No blocking findings.

### P3-CONSTRAINT - Preserve deterministic ordering for exact score ties

Observation: The proposal says `sort_by_dispatch_priority` orders by descending score and uses older `filed_at` first as the tie-break, "making the order total and deterministic" (`bridge/gtkb-bridge-scheduler-lanes-leases-slice-6-001.md:84`). The test plan covers identical score with older `filed_at` first (`bridge/gtkb-bridge-scheduler-lanes-leases-slice-6-001.md:123`), but two entries can still have the same priority and the same `filed_at`.

Deficiency rationale: The live integration will eventually sort bridge entries derived from `bridge/INDEX.md`. If the standalone primitive leaves exact ties implicit, later callers may accidentally rely on container iteration order or lose oldest-first INDEX stability when entries share the same timestamp and priority.

Proposed solution: Implement `sort_by_dispatch_priority` as a stable sort that preserves input order after score and `filed_at` tie-breaks, and document that final tie behavior. Add a focused test where two entries have identical priority and identical `filed_at`, asserting their relative input order is preserved. If Prime prefers a stronger public contract, an optional stable key such as document slug is acceptable, but it must stay deterministic.

Option rationale: Stable input-order tie-breaking keeps the Slice 6 API small and matches the future dispatcher's natural input source, where the bridge index already supplies a deterministic candidate order.

### P4-INFO - Integration remains pending and depends on the corrected lane classifier

Observation: Slice 6 intentionally excludes wiring into `cross_harness_bridge_trigger.py` and `single_harness_bridge_dispatcher.py` (`bridge/gtkb-bridge-scheduler-lanes-leases-slice-6-001.md:96`), while current dispatcher code still uses fixed caps (`scripts/cross_harness_bridge_trigger.py:112`; `scripts/single_harness_bridge_dispatcher.py:72`). The sibling Slice 5 classifier is currently latest `NO-GO`, not implemented.

Deficiency rationale: The standalone module is a valid primitive boundary, but it does not improve live bridge throughput by itself. Treating Slice 6 as completion of the scheduler program would leave the fixed `DEFAULT_MAX_ITEMS = 2` dispatch behavior in place and would also bypass the unresolved lane-classification defects.

Proposed solution: Keep this implementation limited to `scripts/bridge_dispatch_priority.py` and `platform_tests/scripts/test_bridge_dispatch_priority.py`. In the post-implementation report, explicitly state that live dispatch behavior remains unchanged and that final scheduler integration remains pending until Slice 5 is corrected and an integration proposal consumes the scheduler primitives together.

Option rationale: Approving the pure scorer keeps the slice focused and testable. Bundling dispatch integration into this slice would expand target paths beyond the proposal and couple this review to the currently unresolved Slice 5 classifier.

## Positive Confirmations

- Live `bridge/INDEX.md` was reread before verdict; latest status remained `NEW: bridge/gtkb-bridge-scheduler-lanes-leases-slice-6-001.md`.
- `show_thread_bridge.py` reported no drift for the Slice 6 thread.
- The proposal includes project-linkage metadata for active authorization `PAUTH-PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES-BRIDGE-SCHEDULER-PROGRAM-IMPLEMENTATION-AUTHORIZATION`, project `PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES`, and work item `WI-3377`.
- `groundtruth_kb projects authorizations PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES --json` shows that authorization is active and includes `WI-3377`.
- `groundtruth_kb projects show PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES --json` shows `WI-3377` is "Bridge scheduler Slice 6: aging and priority weighting."
- Current state inspection found `scripts/bridge_dispatch_priority.py` and `platform_tests/scripts/test_bridge_dispatch_priority.py` do not yet exist, matching the pre-implementation state.
- Current dispatch state still has fixed caps in both dispatchers (`scripts/cross_harness_bridge_trigger.py:112`; `scripts/single_harness_bridge_dispatcher.py:72`), and this GO does not authorize changing those files in Slice 6.

## Applicability Preflight

- packet_hash: `sha256:a96f43d88c7448c2c5aea9b361c228cfdfd747b23466e88b01b1ea716371d2a2`
- bridge_document_name: `gtkb-bridge-scheduler-lanes-leases-slice-6`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-scheduler-lanes-leases-slice-6-001.md`
- operative_file: `bridge/gtkb-bridge-scheduler-lanes-leases-slice-6-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-bridge-scheduler-lanes-leases-slice-6`
- Operative file: `bridge\gtkb-bridge-scheduler-lanes-leases-slice-6-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate (exit 5) when evidence is absent and no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited. Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Follow-On Constraints for Prime Builder

1. Run `python scripts/implementation_authorization.py begin --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-6` before implementation edits.
2. Keep implementation within `scripts/bridge_dispatch_priority.py` and `platform_tests/scripts/test_bridge_dispatch_priority.py`; do not modify dispatch code in this slice.
3. Preserve the approved public API names: `DEFAULT_PRIORITY_HEADSTART_HOURS`, `DEFAULT_PRIORITY`, `DEFAULT_AGING_RATE_PER_HOUR`, `priority_headstart`, `dispatch_score`, `sort_by_dispatch_priority`, and `select_next`.
4. Preserve the linear effective-age scoring model: `priority_headstart(priority) + aging_rate * age_hours`, with future-dated `filed_at` clamped to zero age.
5. Implement UTC-aware parsing for ISO-8601 strings and aware `datetime` values. Reject or clearly handle naive datetimes; do not let host-local timezone defaults influence scores.
6. Normalize priority labels deterministically before lookup. Unknown or absent priorities may map to `DEFAULT_PRIORITY` as proposed, but lower-case variants such as `p2` should not silently degrade to `P3`.
7. Preserve stable deterministic ordering for exact ties by keeping input order after score and `filed_at` tie-breaks, or by adding an explicitly documented stable key.
8. Include tests T1-T11 from the proposal plus coverage for exact score/timestamp ties, timezone handling, and case-insensitive priority normalization.
9. Re-run and report `python -m pytest platform_tests/scripts/test_bridge_dispatch_priority.py -q`.
10. Re-run and report both bridge preflights in the post-implementation report.
11. In the post-implementation report, state that live dispatch behavior remains unchanged until a later integration proposal wires this module into the dispatch path with the other scheduler primitives.

## Opportunity Radar

No separate advisory was filed. This proposal is itself a deterministic-service step: it turns priority/aging selection into a reusable pure module rather than embedding scoring math directly in dispatch scripts. The material follow-on opportunity is the later integration proposal, which should consume the Slice 2, Slice 3, Slice 4, corrected Slice 5, and Slice 6 primitives together instead of reimplementing scheduler policy inside the dispatcher.

## Commands Executed

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-6
```

Observed: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.

```powershell
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-6
```

Observed: 5 clauses evaluated; `Evidence gaps in must_apply clauses: 0`; `Blocking gaps (gate-failing): 0`; exit 0.

```powershell
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-bridge-scheduler-lanes-leases-slice-6 --format json --preview-lines 420
```

Observed: full chain found with latest live status `NEW` on `bridge/gtkb-bridge-scheduler-lanes-leases-slice-6-001.md`; no drift reported.

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config E:\GT-KB\groundtruth.toml deliberations get DELIB-2182
```

Observed: DELIB-2182 records owner authorization for the full bridge scheduler program and confirms Slice 6 as the aging and priority weighting slice.

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config E:\GT-KB\groundtruth.toml projects authorizations PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES --json
```

Observed: the project authorization is active and includes `WI-3377`.

## Owner Action Required

None.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
