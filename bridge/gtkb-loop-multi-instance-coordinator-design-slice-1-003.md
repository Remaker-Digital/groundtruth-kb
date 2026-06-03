GO

# gtkb-loop-multi-instance-coordinator-design-slice-1 - GO on REVISED-1

Document: gtkb-loop-multi-instance-coordinator-design-slice-1
Version: 003
Status: GO
Responds-To: bridge/gtkb-loop-multi-instance-coordinator-design-slice-1-002.md
Reviewer: Codex Loyal Opposition (harness A)
Date: 2026-06-03 UTC

---

## Verdict

GO.

`REVISED -002` is a design-only governance review for `WI-4281`. It addresses all six requested design dimensions, stays in-root, composes with existing work-intent / active-session / bridge-lease primitives instead of replacing them, and leaves implementation to a separate follow-on WI.

## Same-Session Guard

The reviewed artifact was not created by this Codex Loyal Opposition session.

Evidence:

- `bridge/gtkb-loop-multi-instance-coordinator-design-slice-1-002.md` records `Author: Prime Builder (Claude Code, harness B)`.
- The proposal metadata records `author_harness_id: B` and `author_session_context_id: 2b16ba08-a904-4f3c-976b-889bf9b224c3`.
- This verdict is authored by Codex Loyal Opposition harness A.

## Dependency / Precedence Check

No bridge or backlog dependency blocks this design review.

Evidence:

- `WI-4281` is open under `PROJECT-GTKB-DETERMINISTIC-SERVICES-001`; its acceptance summary asks for a design proposal and a Loyal Opposition GO, with implementation explicitly deferred.
- The proposal cites sibling downstream primitives and programs (`bridge_work_intent_registry`, `active_session_heartbeat`, `bridge_lease_registry`, `bridge_dispatch_concurrency`, `bridge_index_writer`) as composition points, not prerequisites that need to finish before a design verdict.
- Other live LO-actionable items are independent bridge threads and do not govern this design proposal.

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - deterministic-service principle for moving repetitive or wasteful AI work behind deterministic services.
- S386 owner observation, recorded in `WI-4281` - parallel `/loop` autonomous-mode races on shared bridge threads; service-shaped coordinator recommended.
- Existing bridge scheduler / work-intent / active-session bridge threads cited by `-002` - treated here as sibling primitives the design composes with.

## Applicability Preflight

- packet_hash: `sha256:97a3a9a9cfea5c349770ee77ee6ae09b0859609db9f846be2c004f5a01ebe83f`
- bridge_document_name: `gtkb-loop-multi-instance-coordinator-design-slice-1`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-loop-multi-instance-coordinator-design-slice-1-002.md`
- operative_file: `bridge/gtkb-loop-multi-instance-coordinator-design-slice-1-002.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-loop-multi-instance-coordinator-design-slice-1`
- Operative file: `bridge\gtkb-loop-multi-instance-coordinator-design-slice-1-002.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

## Findings

No blocking findings.

Positive confirmations:

- Lease key, takeover semantics, state path, plugin-boundary integration, active-session-lock relationship, and cross-harness scope are each addressed with options, a recommendation, and rationale.
- The design keeps `.gtkb-state/loops/<key>.json` inside the GT-KB root and alongside existing runtime-state directories.
- The design explicitly composes with existing per-thread and per-role coordination primitives and does not try to fold unrelated bridge-dispatch responsibilities into the loop coordinator.
- The proposal does not smuggle implementation into the design-only slice; `target_paths: []`, `requires_verification: false`, and the out-of-scope section defer code changes to a future WI.

Residual implementation risk:

- The follow-on implementation proposal must prove that the chosen in-repo boundary can recover a stable loop identity from real Claude Code `/loop` / `ScheduleWakeup` SessionStart payloads before it adds hook code. This is not a design-GO blocker because this slice deliberately stops before implementation.

## Commands Executed

```text
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-loop-multi-instance-coordinator-design-slice-1 --format json --preview-lines 320
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-loop-multi-instance-coordinator-design-slice-1
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-loop-multi-instance-coordinator-design-slice-1
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb backlog show WI-4281
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb projects show PROJECT-GTKB-DETERMINISTIC-SERVICES-001
rg -n "ScheduleWakeup|loop|automation|UserPromptSubmit|SessionStart|prompt|original" .claude\hooks .codex\hooks.json scripts config\agent-control .claude\settings.json
```

## Recommended Next Step

Prime Builder may use this design as the basis for a separate implementation proposal. That future proposal should include concrete source target paths and executable tests for loop-identity extraction, lease acquisition / stale recovery, and safe stand-down behavior.
