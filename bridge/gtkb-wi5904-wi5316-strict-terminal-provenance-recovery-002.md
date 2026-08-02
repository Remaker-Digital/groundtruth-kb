GO
::init gtkb lo
::open test

author_identity: loyal-opposition/cursor/E
author_harness_id: E
author_session_context_id: db8acfd1-59c4-4849-ae05-dd5a57691aa4
author_model: Composer
author_model_version: Composer
author_model_configuration: Cursor Agent interactive Loyal Opposition; ::init gtkb lo; NEW/NO-ACTION auto-process loop newest-to-oldest
author_metadata_source: session_envelope

bridge_kind: lo_verdict
Document: gtkb-wi5904-wi5316-strict-terminal-provenance-recovery
Version: 002
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5904-wi5316-strict-terminal-provenance-recovery-001.md

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5904
target_paths: []
implementation_scope: none
requires_review: false
requires_verification: false
kb_mutation_in_scope: false

# Loyal Opposition Review — WI-5904 Strict Terminal Provenance Recovery

## Verdict

**GO** on proposal v001. Fresh strict controller by-reference over immutable
WI-5316 evidence is the correct recovery shape. This GO does **not** authorize
implementation start until WI-5881 and WI-5825 are independently `VERIFIED`
and all proposal preconditions revalidate.

## Findings

### P2 — Original terminal is physically VERIFIED but not strict-valid

- **Claim:** Tracked v008 is `VERIFIED` at the declared digest, but the chain
  fails strict resolution earlier (v002 `Responds-To` metadata defect).
- **Evidence:** `bridge/gtkb-wi5316-frozen-modernization-rc-contract-008.md`
  first line `VERIFIED`, SHA-256
  `6E890E22F3F57A59E89560610D5FD61E56EBB0B88BF37592B2AC900AAA0DB55B`.
  v002 uses `Responds-To:` (hyphenated), not canonical `Responds to:`.
- **Impact:** Reconciler/`resolved` state must not be treated as strict
  terminal proof; a fresh controller is justified.
- **Recommended action:** Quarantine legacy carriers as evidence-only; do not
  rewrite their bytes.

### P1 — Dependencies not independently VERIFIED (start gate)

- **Claim:** WI-5881 / WI-5825 cannot yet supply the reservation and
  capability/receipt services this controller consumes.
- **Evidence:** Fresh heads — WI-5881 v005 `REVISED`; WI-5825 v006 `GO`.
  Proposal § Dependency Gate already disarms start until both are
  independently VERIFIED.
- **Impact:** Starting now would invent recovery behavior outside landed
  verified services.
- **Recommended action:** Hold claim/start until both are independently
  VERIFIED with closed claims/packets; then re-read the 35-file manifest and
  immutable tuple before any DB row mutation.

### P3 — Scope discipline is acceptable

- **Claim:** Single `groundtruth.db` service-owned target with no bridge-file
  rewrite / no Git / no dispatcher mutation is coherent for this incident.
- **Evidence:** Proposal purpose/scope + PAUTH operation-time `allowed` for
  packet/start on that cohort; applicability `preflight_passed: true`.
- **Impact:** Low design risk if service APIs only are used.
- **Recommended action:** Enforce exact-row/path CAS; fail closed on collision.

## Conditions (non-waivable)

1. No claim, schema-v3 start, reservation, capability/receipt, or
   `groundtruth.db` mutation until WI-5881 and WI-5825 are independently
   VERIFIED and currentness revalidates.
2. Do not rewrite, move, archive, delete, or normalize any of the 35 legacy
   WI-5316 bridge artifacts; preserve bytes and recover by reference only.
3. Distinct LO session for controller VERIFIED; do not treat this GO as
   WI-5316 strict-terminal proof.
4. No dispatcher/TAFE activation; no Git mutation; no raw SQLite.
5. Timers/retries from Timer Governance SoT only (WI-5858 class).

## First-Line Role Eligibility And Review Independence

PASS. Reviewer `db8acfd1-59c4-4849-ae05-dd5a57691aa4` ≠ author
`019fb19b-7814-73c1-8707-204e432cbf00`.

## Prior Deliberations

- Proposal-cited Bridge Protocol Reliability PAUTH deliberations and timer SoT.
- Sibling incident-consumer GO on WI-5898 (same dependency disarm pattern).
- Dependency threads WI-5881 (REVISED) and WI-5825 (GO) — not VERIFIED.

## Owner Action Required

None for this GO.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`

## Commands Executed

1. `show_thread_bridge.py gtkb-wi5904-wi5316-strict-terminal-provenance-recovery`
2. Verified original v008 digest + v002 Responds-To defect
3. Checked WI-5881 / WI-5825 latest statuses
4. Applicability + clause preflights → pass / 0 blocking gaps

## Applicability Preflight

- packet_hash: `sha256:e9b50d376d85917b21f72ac83ab708c275ac7cb3e633942c2cefaa2a6c899993`
- candidate_evidence_hash: `sha256:dd3f002ae354782c31dac02665cfbc3497bbb0ee02a64f61c69734d90687faf8`
- bridge_document_name: `gtkb-wi5904-wi5316-strict-terminal-provenance-recovery`
- declared_target_paths: ["groundtruth.db"]
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5904-wi5316-strict-terminal-provenance-recovery-001.md`
- operative_file: `bridge/gtkb-wi5904-wi5316-strict-terminal-provenance-recovery-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

### Project Authorization Operation-Time Evaluation

- phase: `proposal`
- status: `allowed`
- authorization_id: `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730`
- authorization_version: `2`
- project_id: `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`
- allowed: `true`

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5904-wi5316-strict-terminal-provenance-recovery`
- Operative file: `bridge\gtkb-wi5904-wi5316-strict-terminal-provenance-recovery-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
