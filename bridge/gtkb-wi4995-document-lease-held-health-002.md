GO

# WI-4995 Document Lease Held Health Classification -- Proposal Review Verdict

bridge_kind: lo_verdict
Document: gtkb-wi4995-document-lease-held-health
Version: 002
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-03 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi4995-document-lease-held-health-001.md (NEW)
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-03T11-44-59Z-loyal-opposition-B-e77180
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code headless bridge auto-dispatch; resolved role loyal-opposition (LO); skills gtkb-bridge + proposal-review
Recommended commit type: fix

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4995-LEASE-HEALTH
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4995

---

## Verdict

**GO.** The proposal is well-scoped, correctly spec-linked, and its core premise
is confirmed against the current dispatcher-health source and the documented live
soak evidence. Both mandatory preflights pass with zero missing required specs and
zero blocking clause gaps. The cited project authorization is active, unexpired,
and correctly scoped to WI-4995 with mutation classes covering the proposed source
and test changes. Implementation may proceed within the declared `target_paths`
after `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4995-document-lease-held-health`.

Three advisory (non-blocking) findings and a block of Prime Builder implementation
context follow. None gate the GO.

## Applicability Preflight

- packet_hash: `sha256:834767c1336fc59b06cab5f5ff35e8e6b908f3bb4520546ae1d42b9791c4d4c6`
- bridge_document_name: `gtkb-wi4995-document-lease-held-health`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi4995-document-lease-held-health-001.md`
- operative_file: `bridge/gtkb-wi4995-document-lease-held-health-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

`missing_required_specs: []` -> the mandatory applicability gate is satisfied. The
three `missing_advisory_specs` are advisory-severity only (artifact-oriented
governance family, matched by generic content tokens) and do not gate the GO;
they are surfaced as advisory finding F1 below.

## Clause Applicability

- Bridge id: `gtkb-wi4995-document-lease-held-health`
- Operative file: `bridge/gtkb-wi4995-document-lease-held-health-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass. Observed exit: 0.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | -- | blocking | blocking |

Zero blocking gaps; all four `must_apply` clauses carry satisfying evidence. The
clause gate is satisfied.

## Prior Deliberations

Semantic `search_deliberations()` was run for two queries ("document lease held
dispatch health false failure" and "dispatch health stale failure_class benign
non-launch"); neither returned an indexed record, consistent with this being a
newly-discovered health-classification residue after the WI-4977 closure rather
than a revisit of a previously-rejected approach.

The proposal's cited prior deliberations were verified to exist in MemBase and are
on-point:

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` -- FOUND; it is also the
  `owner_decision_deliberation_id` recorded on the cited PAUTH. Establishes owner
  authority for governed stability WIs under the dispatcher-modernization project.
- `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN` -- FOUND; the proposal correctly
  commits to not adding any direct harness launch path (honored in Proposed Scope
  and Out of Scope).
- `DELIB-202665265` -- FOUND; earlier owner authorization evidence for creating
  stability WIs discovered during the live soak.
- `bridge/gtkb-wi4977-headless-dispatch-stability-008.md` and
  `bridge/gtkb-wi4994-prime-builder-fanout-dispatcher-001.md` -- the predecessor
  lease-handling closure and the live proposal whose Ollama-D lease exposed the
  B false-failure state.

This defect belongs to the same stale-evidence-vs-benign-current-state family as
`gtkb-wi4718-dispatch-health-benign-cap-false-fail`,
`gtkb-wi4733-dispatch-health-stale-runtime-state`, and
`gtkb-wi4935-dispatch-failover-stale-state-reconciliation`. It is a genuine
uncovered gap, not a duplicate of those (see Premise Verification).

## Specification Linkage Review

All seven cited specifications were confirmed present in MemBase via
`db.get_spec()` (no phantom links):

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` -- FOUND
- `ADR-DISPATCHER-ARCHITECTURE-001` -- FOUND
- `GOV-FILE-BRIDGE-AUTHORITY-001` -- FOUND
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` -- FOUND
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` -- FOUND
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` -- FOUND
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` -- FOUND

The linkage is complete and relevant, and the Specification-Derived Verification
Plan maps each linked spec to a planned test/assertion. Linkage gate satisfied.

## Premise Verification (against live source)

The proposal's claim was verified at the code level, not merely accepted from the
artifact:

1. In `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`,
   `subprocess_execution_failed` is a member of `RUNTIME_FAILURE_CLASSES`
   (line ~58). When present with `has_pending_work` and `not ignore_failure_fields`,
   `_runtime_classification_for_recipient` emits
   `dispatch runtime failure: <recipient> failure_class=subprocess_execution_failed
   with pending_count=<n>` (lines ~931-935), which drives `health_status` to FAIL
   for that finding and produces the reported WARN-level runtime-failure finding.
2. `document_lease_held` does NOT appear anywhere in `bridge_dispatch_config.py`.
   It is absent from `BENIGN_NONLAUNCH_LAUNCH_REASONS`,
   `DISPATCH_BUDGET_BENIGN_LAUNCH_REASONS`, and `RUNTIME_FAILURE_LAUNCH_REASONS`.
   So a benign lease-held non-launch neither emits a finding itself nor is
   recognized as superseding stale failure evidence.
3. `_stale_failure_evidence_reason` (line ~1074) only marks failure evidence as
   ignorable for three conditions: a terminal referenced bridge document, a
   recipient-evidence mismatch, or a dead dispatch run. A current benign
   `document_lease_held` non-launch matches none of these, so `ignore_failure_fields`
   stays False and the stale `failure_class` trips the failure finding.
4. The daemon at `scripts/gtkb_dispatcher_daemon.py` (lines ~805-819) writes the
   benign outcome as `recipient_state["last_result"] =
   runtime.DOCUMENT_LEASE_HELD_RESULT` ("document_lease_held") but leaves any
   prior-cycle `failure_class` populated -- exactly the residue the proposal
   describes.

Conclusion: the defect is real and the reproduction is credible. The root cause is
that a benign current-cycle `document_lease_held` non-launch does not clear or
supersede stale `failure_class` evidence in the health classifier.

## Positive Confirmations

- Status token `NEW` on line 1; `bridge_kind: prime_proposal` (canonical).
- Review independence satisfied: proposal `author_session_context_id`
  `019f247b-4dc8-7b32-a2ab-25839614d33f` (Codex, harness A) differs from this
  reviewer's session context `2026-07-03T11-44-59Z-loyal-opposition-B-e77180`
  (Claude, harness B). Not a self-review.
- Latest thread status is `NEW` (only version 001 exists) -> actionable for LO.
- `target_paths` present as inline JSON; all five paths are inside `E:\GT-KB`
  (In-Root Placement Evidence present).
- `Requirement Sufficiency` subsection present ("Existing requirements sufficient")
  and correct -- accurate health classification is already required by
  `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`; the gap is test/impl coverage, not a
  new requirement.
- `Owner Decisions / Input` section present and accurate. PAUTH
  `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4995-LEASE-HEALTH` verified
  via `db.get_project_authorization`: `status=active`, `expires_at=null`,
  `included_work_item_ids=["WI-4995"]`,
  `allowed_mutation_classes=["bridge","source","tests","dispatcher-health"]`
  (covers the proposed source + test changes), `forbidden_operations` includes
  "direct harness-to-harness launch" (which the proposal explicitly preserves
  against). `scope_summary` matches the proposal intent verbatim.
- Verification plan cites BOTH `ruff check` AND `ruff format --check` (separate
  gates) plus focused pytest -- satisfies the pre-file code-quality gate
  requirement.
- Acceptance criteria are precise and testable, and correctly preserve genuine
  failure detection + lease-held duplicate-launch suppression.

## Advisory Findings (P3 -- non-blocking; do not gate the GO)

### F1 -- Uncited advisory artifact-oriented-governance specs

- Observation: the applicability preflight lists `missing_advisory_specs`:
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`,
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`.
- Rationale: these are advisory-severity, matched only by broad content tokens
  (owner decision, requirement, specification, ADR, DCL, work item). They are not
  load-bearing for this dispatcher-health fix.
- Recommended action: optional. Prime may add them to `Specification Links` in the
  post-implementation report for a fully green advisory preflight, or leave them;
  either is acceptable. Not a NO-GO trigger.

### F2 -- Implement against the actual benign-signal field(s)

- Observation: the live daemon records the benign outcome as
  `recipient_state["last_result"] = "document_lease_held"`
  (`dispatcher_runtime.DOCUMENT_LEASE_HELD_RESULT`), whereas the proposal's soak
  evidence cites `last_launch.reason=document_lease_held`. Both fields may be
  populated on the recipient row depending on the write path.
- Rationale: the fix must key on the field(s) that actually carry the benign
  current-cycle signal so the regression test asserts the real recorded state
  shape. If only `last_result` is set in the reproduced row, a fix that only
  inspects `last_launch.reason` would silently miss.
- Recommended action: in the regression fixture, reproduce the exact recipient-row
  shape from the live soak (both `last_result` and `last_launch.reason` where
  present) and make the benign-supersession logic recognize whichever field(s)
  carry `document_lease_held`. Assert on `gt bridge dispatch health --json` /
  `_runtime_classification_for_recipient` output, not just one field.

### F3 -- Prefer classifier-side benign-supersession over daemon state mutation

- Observation: the proposal keeps "state-writing path, health classification path,
  or both" open, and its Risk section already leans toward preserving failure
  history.
- Rationale: clearing `failure_class` in daemon state risks losing historical
  failure evidence (only partially mitigated by the JSONL history). The existing
  `ignore_failure_fields` / `_stale_failure_evidence_reason` mechanism is the
  established, lower-risk seam for "current benign state supersedes stale evidence"
  -- it is exactly how WI-4718/WI-4733 handled the same class.
- Recommended action (Prime retains implementation choice): prefer extending the
  health classifier so a current benign `document_lease_held` non-launch marks
  stale failure fields ignorable (a new benign-reason set member or a
  `_stale_failure_evidence_reason` branch), emitting the existing
  "stale failure evidence ignored" warning rather than a failure. Reserve daemon
  state mutation for cases where a stale field genuinely must be reset, and keep
  the JSONL failure history intact.

## Prime Builder Implementation Context

| Element | Detail |
|---|---|
| Objective | A recipient row with pending LO work, a benign current `document_lease_held` non-launch, and a stale `failure_class=subprocess_execution_failed` must NOT emit `dispatch runtime failure`; real failures and lease-held duplicate-launch suppression must be preserved. |
| Preconditions | `implementation_authorization.py begin --bridge-id gtkb-wi4995-document-lease-held-health` succeeds against this GO; edits confined to the five `target_paths`. |
| Evidence paths | `bridge_dispatch_config.py`: `RUNTIME_FAILURE_CLASSES` (~L48-62), `BENIGN_NONLAUNCH_LAUNCH_REASONS` (~L73-80), `_runtime_classification_for_recipient` (~L842-1024, failure emission ~L931-935), `_stale_failure_evidence_reason` (~L1074-1091). Daemon: `scripts/gtkb_dispatcher_daemon.py` lease-held write (~L790-819); `scripts/dispatcher_runtime.py` `DOCUMENT_LEASE_HELD_RESULT` (~L350). |
| File touchpoints | `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`, `scripts/gtkb_dispatcher_daemon.py` (only if daemon-side reset is chosen), and the three declared test files. |
| Implementation sequence | (1) Add a narrow benign-supersession branch for `document_lease_held` in the classifier (F3). (2) Add regression coverage reproducing the F2 row shape. (3) Run the three focused test files + ruff check + ruff format --check. |
| Verification steps | The proposal's expected commands: focused pytest across the three test files; `ruff check` and `ruff format --check` on all five paths. Post-impl report must include a spec-to-test mapping row for each linked spec with `Executed=yes`. |
| Rollback | Revert the WI-4995 source/test changes; bridge files, PAUTH, and MemBase records remain append-only audit records. |
| Open decisions | None blocking. F1-F3 are advisory; Prime chooses the fix seam. |

## Commands Executed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4995-document-lease-held-health` -> `preflight_passed: true`, `missing_required_specs: []`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4995-document-lease-held-health` -> exit 0, blocking gaps 0.
- `db.get_spec(...)` for all seven cited specs -> all FOUND.
- `db.get_project_authorization('PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4995-LEASE-HEALTH')` -> active, unexpired, WI-4995, mutation classes bridge/source/tests/dispatcher-health.
- `db.get_project('PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION')` -> active; `WI-4995` present.
- `db.search_deliberations(...)` (two queries) -> no indexed prior-decision conflict.
- `db.get_deliberation(...)` for the three cited DELIB ids -> all FOUND.
- Source inspection of `bridge_dispatch_config.py`, `gtkb_dispatcher_daemon.py`, `dispatcher_runtime.py` to confirm the premise.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
