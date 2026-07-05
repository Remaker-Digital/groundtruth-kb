# OPS Lifecycle And Dispatcher Model Consolidation

Generated: 2026-07-02
Author: Codex Prime Builder
Status: Consolidation report; not implementation authority
Session: 2026-07-02-ops-lifecycle-deliberation

## Claim

The substantive owner-grilling phase for the OPS lifecycle and dispatcher recovery model has reached a natural stopping point. The remaining useful work is formalization: update the governed specifications, bridge protocol language, dispatcher state model, artifact schemas, and tests through the normal bridge process.

This report is not a GO verdict, not an implementation proposal, and not authority to mutate protected source or configuration. It is a concise planning artifact for the next bridge filing.

## Consolidated Model

### 1. Harness State Uses Separate Axes

Harness lifecycle must not collapse installation, dispatch authorization, and health into one state.

- `registration_state = registered | retired`
- `dispatch_state = dispatchable | suspended`
- `active` / `suspended` language means dispatchability only and must have no other meaning.
- Heartbeat/health state is separate from dispatchability and applies from the health monitor perspective: `good | degraded | recovering | failed`.

Key decision anchors include `DELIB-HARNESS-REGISTRATION-STATE-NAMES-20260701`, `DELIB-HARNESS-DISPATCH-STATE-NAMES-20260701`, and the 2026-07-02 OPS lifecycle decision series.

### 2. OPS Work Is Artifact-Centric

No harness/model should directly exchange operational messages with another harness/model. OPS work is initiated by creating governed bridge work items and dispatching them through the dispatcher/bridge/CLI surfaces.

Programmatic initiators and agent initiators produce outwardly standard implementation proposal artifacts. The mechanism is invariant across GT-KB and adopter applications; only the integration point that creates the initial proposal changes.

Decision anchors: `DELIB-HARNESS-OPS-MECHANISM-INVARIANT-INITIATORS-VARY-20260702`, `DELIB-HARNESS-OPS-INITIATORS-CREATE-STANDARD-PROPOSALS-20260702`.

### 3. Context Is Front-Loaded But Time-Bounded

OPS proposals may include programmatically generated diagnostic context so the receiving agent starts with enough current information to act quickly. Generated context must carry freshness metadata and retrieval instructions.

The working TTL principle is: long enough for the agent to retrieve equivalent context and reach first tool use, but not so long that stale programmatic context becomes misleading.

Decision anchors: `DELIB-HARNESS-OPS-PROPOSAL-CURRENT-STATE-CONCISE-SNAPSHOT-20260702`, `DELIB-HARNESS-OPS-PROPOSAL-CURRENT-STATE-FRESHNESS-FIELDS-20260702`.

### 4. LO Controls GO Dispatch Delay

Dispatch delay is selected by the LO in the GO verdict, not by PB. A dispatched GO means explicit implementation authorization.

Nonzero delay requires a reason code plus free-text rationale. The reason-code vocabulary is lower-case, standards-friendly, governed in MemBase/KB, and projected deterministically to dispatcher consumers.

Decision anchors: `DELIB-HARNESS-OPS-DISPATCHED-GO-MEANS-IMPLEMENTATION-AUTHORIZATION-20260702`, `DELIB-HARNESS-OPS-DISPATCH-DELAY-SELECTED-BY-LO-20260702`, `DELIB-HARNESS-GO-DISPATCH-DELAY-REASON-CODE-AND-TEXT-20260702`, `DELIB-HARNESS-GO-DISPATCH-DELAY-VOCAB-AUTHORITY-MEMBASE-20260702`.

### 5. Audit Metadata Is Uniform

Every work item artifact carries producer metadata directly. Lifecycle events carry non-duplicative audit deltas such as actor, event type, correlation id, affected artifact/work item refs, and optional trace/span ids.

Producer and actor type vocabularies are shared. Lifecycle event authority lives in append-only MemBase/KB records with deterministic generated projections.

Decision anchors: `DELIB-BRIDGE-WORK-ITEM-UNIVERSAL-PRODUCER-CONSUMER-METADATA-20260702`, `DELIB-BRIDGE-ARTIFACTS-CARRY-PRODUCER-METADATA-DIRECTLY-20260702`, `DELIB-ACTIVITY-LIFECYCLE-EVENTS-AUTHORITY-MEMBASE-20260702`.

### 6. OPS Artifact Schemas Are Standardized

OPS-generated proposals require the standard bridge status tokens plus sections for Producer Metadata, Subject, Trigger And Evidence, Current State, Intended Implementation, Risk And Impact, Authority And Governance, Verification Plan, Dispatch Delay Recommendation, and Linked Artifacts.

LO verdicts and PB after-action reports also require explicit OPS fields:

- GO: dispatch delay, delay reason, rationale, authorized implementation scope.
- NO-GO: blocking findings, required changes, reason code, resubmission guidance.
- VERIFIED: verified outcome, evidence refs, service-log update confirmation, residual risk.
- PB after-action: implemented actions, scope deviations, verification results, service-log updates, remaining followups.

Decision anchors: `DELIB-HARNESS-OPS-GENERATED-PROPOSAL-REQUIRED-SECTIONS-20260702`, `DELIB-HARNESS-OPS-GO-VERDICT-DISPATCH-AUTHORITY-FIELDS-20260702`, `DELIB-HARNESS-OPS-NO-GO-VERDICT-REQUIRED-FIELDS-20260702`, `DELIB-HARNESS-OPS-VERIFIED-VERDICT-REQUIRED-FIELDS-20260702`, `DELIB-HARNESS-OPS-AFTER-ACTION-REPORT-REQUIRED-FIELDS-20260702`.

### 7. NO-ACTION Is First-Class And PB-Authored

PB may reject implementation of a dispatched GO by filing `NO-ACTION` when the GO is incomplete, fraudulent, malformed, non-authoritative, or outside authorized scope.

`NO-ACTION` is a first-class bridge status token, PB-authored, LO-actionable, and never PB implementation-dispatchable. The report requires rejected GO ref, rejection sequence number, blocking issues, evidence refs, and requested LO action.

LO response is limited to corrected GO, NO-GO against the NO-ACTION, or circuit-breaker OPS escalation.

Decision anchors: `DELIB-HARNESS-OPS-PB-FAIL-CLOSED-NO-ACTION-REPORT-20260702`, `DELIB-HARNESS-OPS-NO-ACTION-FIRST-CLASS-BRIDGE-STATUS-20260702`, `DELIB-HARNESS-NO-ACTION-LO-ACTIONABLE-BRIDGE-ROUTING-20260702`, `DELIB-HARNESS-NO-ACTION-LO-RESPONSE-SET-20260702`.

### 8. Corrected GO Is Fresh Authority

A GO that precedes a NO-ACTION is not dispatchable and not implementable. A later corrected GO is dispatchable as a fresh GO. The implementation-facing PB context should present the current authoritative proposal and fresh GO without prior rejected GO/NO-ACTION history by default.

Supersession references for corrected GO are audit metadata only, not implementation narrative.

Decision anchors: `DELIB-HARNESS-NO-ACTION-PRIOR-GO-NONDISPATCHABLE-SUBSEQUENT-GO-FRESH-AUTHORITY-20260702`, `DELIB-HARNESS-CORRECTED-GO-FRESH-AUTHORITY-PB-CONTEXT-20260702`, `DELIB-HARNESS-CORRECTED-GO-SUPERSESSION-AUDIT-METADATA-ONLY-20260702`.

### 9. Circuit Breaker And Quarantine Are Dispatcher Hygiene

The third NO-ACTION flips the work-item circuit breaker. The original workflow attempt dies and becomes non-dispatchable; the dispatcher creates a separate OPS diagnosis work item. The dispatcher should remain simple: track failures, stop loops, create OPS proposals, and leave recovery strategy to the dispatched OPS agent.

Sequence mismatch is also an OPS quarantine trigger and producer-health signal.

Dispatcher quarantine state is minimal: a non-dispatchable flag plus a reason code. Initial reason codes are `no_action_circuit_breaker` and `sequence_mismatch`.

Decision anchors: `DELIB-HARNESS-OPS-NO-ACTION-CIRCUIT-BREAKER-20260702`, `DELIB-HARNESS-NO-ACTION-THIRD-FLIPS-CIRCUIT-BREAKER-INITIAL-WI-DIES-20260702` (terminology later corrected to supersession only), `DELIB-HARNESS-DISPATCHER-RETRY-SIMPLICITY-OPS-RESPONSIBILITY-20260702`, `DELIB-HARNESS-WORK-ITEM-SEQUENCE-MISMATCH-OPS-QUARANTINE-20260702`, `DELIB-HARNESS-ARTIFACT-QUARANTINE-REASON-CODES-20260702`.

### 10. Supersede, Not Resurrect

Failed original work items are not resumed. There is no `resumed_original_work_item` mechanism.

OPS remediation final disposition is limited to:

- `superseded_by_new_work_item`
- `abandoned_unrecoverable`

Superseding work items are completely fresh authorization flows. They start as standard `NEW` proposals with their own LO review and GO. They inherit no implementation authority, dispatchability, claims, or GO status from the failed work item.

Decision anchors: `DELIB-HARNESS-OPS-REMEDIATION-FINAL-DISPOSITION-EXCLUDES-RESUME-20260702`, `DELIB-HARNESS-OPS-SUPERSEDE-NOT-RESURRECT-TERMINOLOGY-20260702`, `DELIB-HARNESS-OPS-SUPERSEDING-WORK-ITEM-FRESH-AUTHORIZATION-20260702`.

### 11. Ordinary Bridge Artifacts Stay Clean

Implementation-facing bridge artifacts must not carry OPS failure lineage, recovery lineage, supersession metadata, prior-version context, or previous work items with the same content and intent. That information is diagnostic noise for an ordinary PB implementer.

OPS lineage belongs in OPS records, service logs, and dispatcher audit records.

Decision anchors: `DELIB-HARNESS-BRIDGE-ARTIFACTS-EXCLUDE-OPS-RECOVERY-LINEAGE-20260702`, `DELIB-HARNESS-OPS-LINEAGE-LIVES-IN-AUDIT-NOT-BRIDGE-20260702`.

### 12. OPS-Diagnosis Work Items Are The Narrow Exception

OPS-diagnosis work items may include failure lineage and recovery context because their purpose is diagnosing an orthogonal workflow failure.

They require a lean `diagnostic_context` section containing:

- `failed_work_item_id`
- `triggering_artifact_id`
- `failure_reason_code`
- `failure_count`
- audit/log references

Audit/log evidence is reference-first. Short embedded excerpts are allowed only when needed for immediate orientation.

Decision anchors: `DELIB-HARNESS-OPS-DIAGNOSIS-WORK-ITEMS-MAY-INCLUDE-LINEAGE-20260702`, `DELIB-HARNESS-OPS-DIAGNOSTIC-CONTEXT-REQUIRED-FIELDS-20260702`, `DELIB-HARNESS-OPS-DIAGNOSTIC-CONTEXT-AUDIT-REFS-BY-DEFAULT-20260702`.

## Proposed Formalization Slices

### Slice 1: Vocabulary And State Model Specs

Create or update governed specs for:

- `registration_state`
- `dispatch_state`
- heartbeat/health states
- artifact quarantine reason codes
- GO dispatch-delay reason codes
- OPS remediation final dispositions

Acceptance: canonical vocabularies live in MemBase/KB or formal specs; dispatcher projections are generated from them; semantic changes require bridge governance.

### Slice 2: Bridge Protocol Extensions

Update the bridge protocol to define:

- `NO-ACTION` as a PB-authored, LO-actionable status token.
- routing rules for latest `NO-ACTION`.
- corrected GO behavior after NO-ACTION.
- monotonic `work_item_sequence_number`.
- prior GO non-dispatchability after NO-ACTION.
- clean implementation-facing context rules.

Acceptance: protocol text and tests prove `NO-ACTION` is not PB implementation-dispatchable, and corrected GO is fresh authority.

### Slice 3: Dispatcher Quarantine And Circuit Breaker

Implement dispatcher state and behavior for:

- third-NO-ACTION circuit breaker.
- sequence mismatch quarantine.
- minimal non-dispatchable flag plus reason code.
- claim release for the preceding artifact when a failed workflow attempt dies.
- separate OPS diagnosis work item creation.

Acceptance: focused dispatcher tests cover circuit breaker, quarantine reason, claim release, and OPS proposal creation without retry-strategy complexity.

### Slice 4: OPS Proposal And Verdict Schemas

Implement schema/helpers/templates for:

- OPS-generated proposal sections.
- producer metadata baseline.
- lifecycle event metadata.
- GO/NO-GO/VERIFIED required OPS fields.
- PB OPS after-action report required fields.
- OPS-diagnosis `diagnostic_context`.

Acceptance: validators reject missing required sections/fields and allow reference-first evidence with short excerpts only when orientation needs are stated.

### Slice 5: Context Packaging And TTL

Add programmatic context-package generation for OPS diagnosis work items:

- generated_at
- expires_at
- source_refs
- retrieval instructions
- concise current-state snapshot

Acceptance: generated context is authoritative only within TTL and includes instructions for refreshing from canonical sources.

### Slice 6: Service Logs, Audit Records, And Dashboard Projection

Implement append-only service-log/dispatcher audit records for:

- lineage for failed and superseded work items.
- quarantine events.
- NO-ACTION count events.
- OPS diagnosis creation.
- remediation final disposition.

Acceptance: ordinary bridge artifacts stay lineage-free; OPS/audit surfaces retain enough lineage for diagnosis and historical analysis.

## Proposed Bridge Filing Shape

Recommended first filing: a scoping/formalization bridge proposal, not source implementation.

Suggested binding if the owner accepts the discovery-only fit:

- Project: `PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY`
- Work Item: `WI-4911`
- Project Authorization: `PAUTH-PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY-DELIBERATION-ADR-DRAFTING`

Reason: this PAUTH covers governance-only formal ADR/DCL/GOV candidate drafting for `WI-4911` and forbids source implementation, substrate migration, and protected-file mutation. That matches the immediate next step: formalize the decision set into candidate specs and an implementation plan.

If the next step is actual source implementation, create a fresh implementation work item and PAUTH under a more exact implementation project such as bridge protocol reliability, dispatcher reliability, or typed artifact flow engine. Do not implement source changes under the discovery-only PAUTH.

Suggested scoping slug:

- `gtkb-ops-lifecycle-dispatcher-model-formalization`

Likely target surfaces for the later implementation proposal:

- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/canonical-terminology.md`
- dispatcher and bridge CLI/runtime modules under `groundtruth-kb/src/groundtruth_kb/`
- dispatcher/bridge scripts under `scripts/`
- focused tests under `platform_tests/scripts/` and `platform_tests/groundtruth_kb/`
- MemBase specs/vocabulary records

## Verification Plan For Later Implementation

Minimum focused checks should include:

- Bridge status transition tests for `NO-ACTION`.
- Dispatcher routing tests proving `NO-ACTION` routes only to LO.
- Circuit-breaker tests proving third NO-ACTION makes the workflow non-dispatchable and creates OPS diagnosis work.
- Sequence mismatch tests proving quarantine and OPS diagnosis creation.
- Corrected GO tests proving fresh authority and no implementation-facing lineage.
- Clean bridge artifact tests proving ordinary PB dispatch envelopes exclude OPS lineage.
- OPS-diagnosis tests proving `diagnostic_context` carries required fields.
- Vocabulary-governance tests proving new reason codes require governed updates.
- Existing dispatcher transaction and cross-harness protocol parity tests.

Known current verification caveat from earlier dispatcher work in this session: `platform_tests/scripts/test_cross_harness_protocol_parity.py` had stale active/suspended assumptions and a Codex hook assertion failure. Do not treat that file as clean until repaired or scoped out by LO.

## Recommendation

Stop grilling. File a governance-only scoping proposal that converts this decision set into formal specs and an implementation-slicing plan. After LO review, create a fresh implementation work item/PAUTH for the source changes rather than using the discovery-only authorization for implementation.
