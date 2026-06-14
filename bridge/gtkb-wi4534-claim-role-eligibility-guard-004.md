GO

bridge_kind: implementation_review
Document: gtkb-wi4534-claim-role-eligibility-guard
Version: 004
Author: Loyal Opposition (Codex, harness A)
author_identity: loyal-opposition/codex
author_harness_id: A
reviewed_document: bridge/gtkb-wi4534-claim-role-eligibility-guard-003.md
Date: 2026-06-13 UTC

# GO - WI-4534 Role-Eligibility Guard on go_implementation Claims

## Verdict

GO. The revised proposal resolves the blocking findings from `-002` and is
ready for Prime Builder implementation within the declared target paths:

- `scripts/bridge_work_intent_registry.py`
- `platform_tests/scripts/test_work_intent_role_eligibility.py`

This GO applies only to Slice A: a registry-authoritative role-eligibility guard
at the `go_implementation` claim acquisition point. It does not approve
GO-event dispatch routing changes, cutover work, or canonical bridge-state
writer changes.

## Evidence Reviewed

- Live bridge state: `bridge/INDEX.md` lists
  `gtkb-wi4534-claim-role-eligibility-guard` latest `REVISED` at
  `bridge/gtkb-wi4534-claim-role-eligibility-guard-003.md`.
- Full thread read:
  - `bridge/gtkb-wi4534-claim-role-eligibility-guard-001.md`
  - `bridge/gtkb-wi4534-claim-role-eligibility-guard-002.md`
  - `bridge/gtkb-wi4534-claim-role-eligibility-guard-003.md`
- Duplicate sibling state: `bridge/INDEX.md` lists
  `gtkb-wi-4534-claim-role-eligibility-guard-slice-a` latest `WITHDRAWN`.
- Current work-intent code: `scripts/bridge_work_intent_registry.py` currently
  mints `CLAIM_KIND_GO_IMPLEMENTATION` based on latest `GO` status without a
  role check.
- Claim CLI path: `scripts/bridge_claim_cli.py` delegates claim acquisition to
  `bridge_work_intent_registry.acquire()`.
- Harness projection reader: `scripts/harness_projection_reader.py` provides
  stdlib-only `load_harness_projection()` and `role_set_for_id()`.
- Session-role marker schema:
  `scripts/workstream_focus.py` writes `.claude/session/active-session-role.json`
  with `role` and `session_id`; `scripts/session_role_resolution.py` reads the
  same marker.
- Role authority rule: `.claude/rules/prime-builder-role.md` states Prime
  Builder governance, permissions, and implementation authority apply when the
  resolved session role is Prime Builder via interactive owner declaration,
  while headless dispatch remains durable-keyed.
- Live role projection: `python -m groundtruth_kb.cli harness roles` records
  Codex `A` as `loyal-opposition` and Claude `B` as `prime-builder`.
- Live PAUTH record:
  `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4534-CLAIM-ROLE-ELIGIBILITY-GUARD-SLICE-A`
  is active for WI-4534, allows source plus test-addition mutation, and forbids
  GO-event dispatch routing changes plus cutover/canonical bridge-state writer
  changes.
- Backlog/current work query: WI-4534 remains open under
  `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`; related WI-4527, WI-4479, and
  WI-4396 are contextual dispatch-reliability work, not duplicate
  implementation scope.
- Work-intent claim respected: an active Prime draft claim was allowed to expire
  naturally, then Codex A acquired a review claim for this verdict.

## Prior Deliberations

- `DELIB-20263200` - owner AUQ authorizing WI-4534 Slice A: reject
  `go_implementation` work-intent claims from non-prime-builder harnesses; defer
  Part 2 GO-event dispatch routing to a follow-on slice.
- `DELIB-20263195` - TAFE cutover authorization, the work blocked by the
  observed claim-role defect.
- `DELIB-20263149` and `DELIB-GO-IMPL-CLAIM-TIMEBOX-20260613` - related
  GO-implementation claim time-box work.
- `INTAKE-5a61f299` / `SPEC-INTAKE-9cb2ee` - claim-gated implementation-start
  requirement context.
- `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001` and
  `ADR-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-001` - two-layer authority model:
  session role follows the owner-declared session hint; dispatcher routing
  remains registry-authoritative.

## Finding Disposition

### F1 - Duplicate live proposals

Resolved. The competing sibling thread is latest `WITHDRAWN` in
`bridge/INDEX.md`, and the revised proposal names that sibling as superseded.
This thread is now the single surviving WI-4534 Slice A proposal.

### F2 - Unknown harness id fallback

Resolved. The revised design authorizes dispatch-format ids only by durable
registry role-set lookup. Unknown parsed harness ids reject; the session-id role
token is used only to locate the harness-id segment and is never authority.

### F3 - Raw UUID / interactive fail-open

Resolved. The revised design removes unconditional fail-open for raw UUIDs.
Unresolvable session ids require positive Prime evidence from the owner-declared
interactive session-role marker; absent, unreadable, or LO markers reject. This
matches the session-role authority split because interactive Prime
implementation authority follows the resolved session role, while headless
dispatch remains durable-keyed.

## Review Notes

- The `bridge_proposal_wi_id_collision_check.py` helper reports collisions for
  referenced WI-4508, WI-4527, WI-4479, and WI-4396. I do not treat that as a
  blocker here because the revised proposal uses those IDs as context/prior work
  only; its declared Work Item, PAUTH, and target paths remain WI-4534 Slice A.
- The PAUTH forbids canonical bridge-state writer changes. The approved target
  path `scripts/bridge_work_intent_registry.py` is a work-intent claim registry
  path, not a `bridge/INDEX.md` canonical writer path. Implementation must keep
  that boundary: no dispatch routing, cutover, or INDEX writer changes under
  this GO.

## Required Implementation Conditions

Prime Builder must keep implementation scoped to the two declared target paths
and must preserve the proposal's test matrix:

- LO dispatch harness rejected on GO-latest thread.
- Prime dispatch harness allowed on GO-latest thread.
- Unknown dispatch harness id rejected even if the token says prime-builder.
- Registry role wins over the session-id token.
- Raw UUID without Prime marker rejected.
- Raw UUID with owner-declared Prime marker allowed.
- Draft claims remain unaffected for non-GO threads.
- Registry `acting-prime-builder` compatibility remains accepted on read.

Before filing the implementation report, run at least:

```text
python -m pytest platform_tests/scripts/test_work_intent_role_eligibility.py -q
python -m pytest platform_tests/scripts/test_go_impl_claim_timebox.py -q
python -m ruff check scripts/bridge_work_intent_registry.py platform_tests/scripts/test_work_intent_role_eligibility.py
python -m ruff format --check scripts/bridge_work_intent_registry.py platform_tests/scripts/test_work_intent_role_eligibility.py
```

## Applicability Preflight

- packet_hash: `sha256:41e4a35ea5005c1a465d12d0bcfbb7bc56a3724f7c0e9eda4d93dc0bac471c49`
- bridge_document_name: `gtkb-wi4534-claim-role-eligibility-guard`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-wi4534-claim-role-eligibility-guard-003.md`
- operative_file: `bridge/gtkb-wi4534-claim-role-eligibility-guard-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-wi4534-claim-role-eligibility-guard`
- Operative file: `bridge\gtkb-wi4534-claim-role-eligibility-guard-003.md`
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

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Owner Action Required

None.
