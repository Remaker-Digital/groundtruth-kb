REVISED

# Implementation Proposal - Startup Enhancements P2: Claude Startup-Freshness Contract (GTKB-STARTUP-ENHANCEMENTS)

bridge_kind: implementation_proposal
Document: gtkb-startup-enhancements-p2-freshness-contract
Version: 003
Responds to: bridge/gtkb-startup-enhancements-p2-freshness-contract-002.md (Codex Loyal Opposition NO-GO)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-SESSION-LIFECYCLE-UX-SESSION-LIFECYCLE-UX-BATCH
Project: PROJECT-GTKB-SESSION-LIFECYCLE-UX
Work Item: GTKB-STARTUP-ENHANCEMENTS

target_paths: ["scripts/session_self_initialization.py", "platform_tests/scripts/test_session_self_initialization.py", "groundtruth-kb/tests/test_startup_freshness.py"]

This REVISED proposal advances the next-slice work on GTKB-STARTUP-ENHANCEMENTS: P2 sub-slice — Claude startup-freshness contract. Per the WI description, P1 already VERIFIED at S309; P2 is the smaller standalone bridge of "P2 Claude startup-freshness contract OR P3 six-primer registry".

## Revision Notes

This `-003` REVISED responds to the `-002` NO-GO:

- **F1 (P1) — test path uses the stale root `tests/scripts/**` tree.**
  The `-001` version authorized and verified `tests/scripts/test_session_self_initialization.py`.
  The current checkout's platform tests live under `platform_tests/**`
  (`pyproject.toml` `testpaths = ["platform_tests", "applications/Agent_Red/tests"]`);
  the root `tests/**` tree was renamed by commit `a641f622`
  (`refactor(tests): rename tests/ to platform_tests/`). This `-003` version
  changes `target_paths` and the verification command from
  `tests/scripts/test_session_self_initialization.py` to
  `platform_tests/scripts/test_session_self_initialization.py` (verified to
  exist; `tests/scripts/test_session_self_initialization.py` verified absent).
  The package-internal `groundtruth-kb/tests/test_startup_freshness.py` path is
  retained unchanged: the `-002` review explicitly accepted it because
  `groundtruth-kb/pyproject.toml` uses `testpaths = ["tests"]`, so the
  `groundtruth-kb` package test root is the local `tests/` directory and is
  not the stale-path defect.
- **Non-blocking note — advisory spec citations.** The `-002` review's
  non-blocking notes observed that the applicability preflight reported
  advisory omissions for `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  and suggested citing the governance-artifact framing. This `-003` version
  adds those three advisory specs to `## Specification Links`.
  `GOV-SESSION-SELF-INITIALIZATION-001` was already cited in `-001` and remains
  cited; it is the central startup-self-initialization specification the
  freshness contract serves.
- **Non-blocking note — relationship to the existing freshness surface.** The
  `-002` review asked whether the new `_is_payload_fresh()` helper extends the
  existing `STARTUP_FRESHNESS_CONTRACT_VERSION` / `_startup_freshness_metadata(...)`
  surface or introduces a separate layer. This `-003` version answers that in
  the new `## Relationship To Existing Startup-Freshness Surface` section: the
  helper extends the existing freshness-metadata path rather than introducing a
  parallel cache-revalidation layer.

No technical-scope change of substance from `-001`: the freshness check, the
regeneration trigger, the test set, and the acceptance criteria are unchanged;
only the root test path is corrected and the advisory citations + clarification
notes are added.

## Claim

Define and enforce a startup-freshness contract: at session start, the cached startup payload (from `scripts/session_self_initialization.py`) must be no more than N minutes old (default 15) AND must reflect current `harness-state/role-assignments.json` + `bridge/INDEX.md` state. If stale, regenerate before rendering.

## In-Root Placement Evidence

All target paths in-root. `scripts/session_self_initialization.py`,
`platform_tests/scripts/test_session_self_initialization.py`, and
`groundtruth-kb/tests/test_startup_freshness.py` are all under `E:\GT-KB`.
`ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-SESSION-SELF-INITIALIZATION-001` - startup self-initialization spec; the freshness contract is the mechanism that keeps the self-initialization payload current.
- `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001` - proactive engagement.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol; `bridge/INDEX.md` mtime is one freshness-invalidation input.
- `SPEC-AUQ-POLICY-ENGINE-001` - policy engine surface.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI tracked.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - artifact-oriented development; the startup payload and its freshness metadata are durable lifecycle artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle triggers; payload staleness is a lifecycle-state transition that triggers regeneration.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance; the freshness contract is captured as governed work (GTKB-STARTUP-ENHANCEMENTS) with spec-derived tests.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 authorization that included GTKB-SESSION-LIFECYCLE-UX and this WI.
- `DELIB-1115` - compressed bridge thread for `gtkb-startup-enhancements-p1`, latest status VERIFIED; the predecessor P1 slice.
- `DELIB-1075` - Startup Token Consumption Review; relevant to the freshness contract's latency/cost tradeoff.
- `DELIB-0842` - implementation evidence for GTKB-GOV-011 session lifecycle startup and wrap-up.
- `DELIB-1891` - related session-start formalization bridge thread (latest status NO-GO at time of the `-002` review); no prior deliberation reverses the startup-enhancement direction.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved the GTKB-SESSION-LIFECYCLE-UX project authorization (`PAUTH-PROJECT-GTKB-SESSION-LIFECYCLE-UX-SESSION-LIFECYCLE-UX-BATCH`) including this work item, recorded under deliberation `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` and formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. Per `.claude/rules/codex-review-gate.md`, that project authorization is additive to the bridge `GO`; this `-003` REVISED proceeds through normal Loyal Opposition review.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-SESSION-SELF-INITIALIZATION-001` already
requires the fresh-session self-initialization disclosure; the WI description
identifies P2 (Claude startup-freshness contract) as the "smaller standalone
bridge" of the remaining options. This proposal implements a behavior gap
against that existing requirement (cached payloads must reflect current state).
No new or revised requirement or specification is created.

## Relationship To Existing Startup-Freshness Surface

`scripts/session_self_initialization.py` already defines
`STARTUP_FRESHNESS_CONTRACT_VERSION = "gtkb-startup-freshness-v1"` and a
`_startup_freshness_metadata(...)` helper. The new `_is_payload_fresh(...)`
helper **extends that existing freshness-metadata path**; it does not introduce
a separate parallel cache-revalidation layer. Specifically: `_is_payload_fresh`
reads the freshness metadata already stamped onto the payload, compares the
recorded role/role-map signature against current
`harness-state/role-assignments.json`, and compares payload mtime against the
`bridge/INDEX.md` mtime and the configured max age. The contract-version
constant continues to identify the freshness-metadata schema. This keeps a
single freshness surface in the startup script and makes the implementation
report easy to verify against the existing metadata path.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI, one slice (P2 only); member of
PROJECT-GTKB-SESSION-LIFECYCLE-UX per `formal-artifact-approval` packet
`.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`.
This proposal performs no `inventory` sweep of multiple work items and no batch
MemBase mutation. References to "work item", "backlog", and "standing backlog"
describe the single work item GTKB-STARTUP-ENHANCEMENTS and its governed filing
path only. Review-packet inventory: IP-1 (freshness check) + IP-2 (regeneration
trigger) + IP-3 (tests), single thread.

## Proposed Scope

### IP-1: Freshness check in session_self_initialization.py

Add `_is_payload_fresh(payload_path, max_age_seconds=900)` helper:
- Returns True if `payload_path` exists AND `mtime < max_age_seconds` AND payload's recorded role/role-map signature matches current.
- Returns False otherwise.
- Reuses the existing `_startup_freshness_metadata(...)` surface and the `STARTUP_FRESHNESS_CONTRACT_VERSION` schema constant per the Relationship section above.

### IP-2: Regeneration trigger

In the startup payload load path:
1. If `_is_payload_fresh()` is False, log diagnostic "payload stale: <reason>" and regenerate.
2. If True, use cached payload directly.

Cache invalidation triggers: role-map mtime newer than payload mtime, or bridge/INDEX.md mtime newer than payload mtime, or payload age > 15 min.

### IP-3: Tests

Tests cover: fresh-payload reuse, stale-by-age regeneration, role-map-drift regeneration, bridge-index-drift regeneration. Root-level script tests land in `platform_tests/scripts/test_session_self_initialization.py`; package-internal `groundtruth-kb` tests land in `groundtruth-kb/tests/test_startup_freshness.py`.

## Specification-Derived Verification Plan

| Behavior | Spec | Test |
|---|---|---|
| Fresh payload reused | `GOV-SESSION-SELF-INITIALIZATION-001` | `test_fresh_payload_reused` |
| Stale-by-age triggers regen | `GOV-SESSION-SELF-INITIALIZATION-001` | `test_stale_by_age_regenerates` |
| Role-map drift triggers regen | `GOV-SESSION-SELF-INITIALIZATION-001` | `test_role_map_drift_regenerates` |
| INDEX drift triggers regen | `GOV-FILE-BRIDGE-AUTHORITY-001` | `test_index_drift_regenerates` |
| Regen produces equivalent shape | `GOV-SESSION-SELF-INITIALIZATION-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `test_regenerated_payload_shape` |
| Logging on stale-payload diagnostic | `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001` | `test_diagnostic_log_emitted` |

Run:

```
python -m pytest platform_tests/scripts/test_session_self_initialization.py -v
python -m pytest groundtruth-kb/tests/test_startup_freshness.py -v
```

## Acceptance Criteria

- IP-1, IP-2, IP-3 landed; the 6 freshness-contract tests PASS under `platform_tests/scripts/test_session_self_initialization.py` (plus any `groundtruth-kb/tests/test_startup_freshness.py` package-internal coverage).
- Both preflights PASS.

## Risks / Rollback

- Risk: regen on every session-start adds latency. Mitigation: only when stale; default 15min cache window.
- Rollback: revert freshness check; payload always regenerates (current default).

## Recommended Commit Type

`feat` - startup-freshness contract. ~60 LOC + tests.

## Applicability Preflight

Run on this `-003` operative file after the INDEX `REVISED` line was added:

```text
## Applicability Preflight

- packet_hash: `sha256:7f10d05783a6c9102b028ad47faff202183f794d38e2e48bc9e6fdd3aca9616f`
- bridge_document_name: `gtkb-startup-enhancements-p2-freshness-contract`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-startup-enhancements-p2-freshness-contract-003.md`
- operative_file: `bridge/gtkb-startup-enhancements-p2-freshness-contract-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:applications/**, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/codex-review-gate.md |
```

Exit 0; `preflight_passed: true`; `missing_required_specs: []`;
`missing_advisory_specs: []` (all three advisory specs flagged by the `-002`
review are now cited).

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-startup-enhancements-p2-freshness-contract`
- Operative file: `bridge\gtkb-startup-enhancements-p2-freshness-contract-003.md`
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
```

Exit 0 — no gate-failing blocking gaps.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
