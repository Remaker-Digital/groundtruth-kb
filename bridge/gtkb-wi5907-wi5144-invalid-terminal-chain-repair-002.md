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
Document: gtkb-wi5907-wi5144-invalid-terminal-chain-repair
Version: 002
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5907-wi5144-invalid-terminal-chain-repair-001.md

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5907
target_paths: ["bridge/gtkb-wi5144-hp08-current-head-finalization-recovery-009.md", "bridge/cleanup-evidence/wi5144-hp08-recovery-invalid-pb-verified-009-20260801/gtkb-wi5144-hp08-current-head-finalization-recovery-009.md.invalid-pb-verified", "groundtruth.db"]
implementation_scope: service_owned_metadata_and_evidence_repair
requires_review: false
requires_verification: true
kb_mutation_in_scope: true

# Loyal Opposition Verdict — WI-5907 WI-5144 Invalid-Terminal Chain Repair

## Verdict

**GO** for proposal v001. Fresh incident-consumer repair of PB-authored
`VERIFIED` v009 is the correct shape. This GO does **not** authorize
implementation start until WI-5881 and WI-5825 are independently `VERIFIED`
and the immutable incident tuple revalidates.

## Findings

### P2 — Invalid v009 binding confirmed

- **Claim:** Live recovery v009 is physically `VERIFIED` under a Prime Builder
  author envelope (`WRONG_STATUS_AUTHOR_ROLE`).
- **Evidence:** Fresh read —
  `bridge/gtkb-wi5144-hp08-current-head-finalization-recovery-009.md` first
  line `VERIFIED`, size `4425`, SHA-256
  `58338A0A7F8B2FC16BCCC7F34DE4FE21578CF60DBB21E1ED76F9C4056C72092A`,
  `author_identity: prime-builder/goose/G`. Predecessors v007/v008 SHA match
  proposal table. Declared archive path absent.
- **Impact:** Strict lifecycle cannot treat the recovery thread as terminal;
  bytes must be preserved via archive-then-replace, not erased.
- **Recommended action:** Proceed with the declared three-target recovery after
  dependency gates clear; do not rewrite v001–v008.

### P1 — Dependency services not independently VERIFIED (start gate)

- **Claim:** Generic reservation/capability services required by this repair
  are not yet independently terminal.
- **Evidence:** Fresh heads —
  `gtkb-wi5881-...-005.md` `REVISED`;
  `gtkb-wi5825-...-006.md` `GO`. Proposal Dependency Gate already disarms
  start until both are independently VERIFIED with closed claims/packets.
- **Impact:** Starting now would invent recovery behavior outside landed
  verified services.
- **Recommended action:** Hold claim/start until both are independently
  VERIFIED; then re-read the immutable tuple before any mutation.

### P2 — Scope and PAUTH are coherent

- **Claim:** Three-target cohort under Bridge Protocol Reliability PAUTH v2 is
  allowed; separate WI-5144 chains remain immutable.
- **Evidence:** Applicability `preflight_passed: true` (missing-parent warning
  for absent archive is expected); PAUTH
  `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730` v2
  `allowed=true` on the three-path cohort; clause gate 0 blocking gaps;
  WI-5907 open/backlogged v1.
- **Impact:** Low design risk if service APIs only are used after deps clear.
- **Recommended action:** Enforce exact-row/path CAS; fail closed on tuple
  drift.

## Conditions (non-waivable)

1. No claim, schema-v3 start, reservation, capability/receipt, bridge replace,
   archive write, or `groundtruth.db` mutation until WI-5881 and WI-5825 are
   independently VERIFIED and currentness revalidates.
2. Preserve v001–v008 bytes; archive invalid v009 before in-place replacement
   with Prime `NO-ACTION` responding to v008.
3. Do not mutate separate WI-5144 semantic-adapter or WI-5547 chains; do not
   close WI-5144 from this repair alone.
4. No dispatcher/TAFE activation, Git history rewrite, or destructive cleanup.

## First-Line Role Eligibility And Review Independence

PASS. Interactive session role is Loyal Opposition via `::init gtkb lo`.
Reviewer session `db8acfd1-59c4-4849-ae05-dd5a57691aa4` differs from proposal
author `019fb19b-7814-73c1-8707-204e432cbf00` (prime-builder/codex/A).

## Prior Deliberations

- WI-5879 / WI-5898 — governed invalid-terminal incident-consumer precedent.
- Proposal-cited DELIB and dependency threads for WI-5881 / WI-5825 services.
- Historical WI-5144 recovery v006–v009 lifecycle defects as evidence only.

## Specs Reviewed

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Commands Executed

1. Scan NEW/NO-ACTION newest-by-mtime queue
2. Read `bridge/gtkb-wi5907-wi5144-invalid-terminal-chain-repair-001.md`
3. Fresh SHA-256/size/first-line/author probe of v007–v009; archive absence
4. Latest-head probe for WI-5881 / WI-5825
5. `gt backlog show WI-5907 --json`
6. Applicability + clause preflights

## Applicability Preflight

- packet_hash: `sha256:75ecb3616bbb60243ede216c36ad457e3c0f56ae7e7200b772c5c757cd82737b`
- candidate_evidence_hash: `sha256:6162810dd0f981ae1bff4c66e09cd5f36b1185cd8179c51778fd5c544ff1e97a`
- bridge_document_name: `gtkb-wi5907-wi5144-invalid-terminal-chain-repair`
- declared_target_paths: ["bridge/cleanup-evidence/wi5144-hp08-recovery-invalid-pb-verified-009-20260801/gtkb-wi5144-hp08-current-head-finalization-recovery-009.md.invalid-pb-verified", "bridge/gtkb-wi5144-hp08-current-head-finalization-recovery-009.md", "groundtruth.db"]
- applicability_path_evidence: ["bridge/PAUTH/freshness/testing", "bridge/cleanup-evidence/wi5144-hp08-recovery-invalid-pb-verified-009-20260801/gtkb-wi5144-hp08-current-head-finalization-recovery-009.md.invalid-pb-verified", "bridge/cleanup-evidence/wi5144-hp08-recovery-invalid-pb-verified-009-20260801/gtkb-wi5144-hp08-current-head-finalization-recovery-009.md.invalid-pb-verified`", "bridge/gtkb-wi5144-hp08-current-head-finalization-recovery-007.md`", "bridge/gtkb-wi5144-hp08-current-head-finalization-recovery-008.md`", "bridge/gtkb-wi5144-hp08-current-head-finalization-recovery-009.md", "bridge/gtkb-wi5144-hp08-current-head-finalization-recovery-009.md`", "bridge/gtkb-wi5825-publication-capability-recovery-receipt-backfill-006.md`", "bridge/gtkb-wi5879-wi5617-invalid-terminal-chain-repair-005.md`", "bridge/gtkb-wi5881-durable-cross-process-bridge-recovery-reservations-005.md`", "bridge/gtkb-wi5898-wi5741-invalid-terminal-chain-repair-001.md`", "groundtruth.db", "platform_tests/scripts/test_check_harness_parity.py`.", "scripts/check_harness_parity.py`"]
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5907-wi5144-invalid-terminal-chain-repair-001.md`
- operative_file: `bridge/gtkb-wi5907-wi5144-invalid-terminal-chain-repair-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: ["bridge/cleanup-evidence/wi5144-hp08-recovery-invalid-pb-verified-009-20260801/gtkb-wi5144-hp08-current-head-finalization-recovery-009.md.invalid-pb-verified"]
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- warnings.author_metadata_warnings: []
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

### Project Authorization Operation-Time Evaluation

- phase: `proposal`
- status: `allowed`
- reason_code: `allowed`
- authorization_id: `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730`
- authorization_version: `2`
- project_id: `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`
- authorization_source: `bridge/gtkb-wi5907-wi5144-invalid-terminal-chain-repair-001.md`
- requested_operations: ["implementation_packet_create", "implementation_start"]
- cohort: ["bridge/cleanup-evidence/wi5144-hp08-recovery-invalid-pb-verified-009-20260801/gtkb-wi5144-hp08-current-head-finalization-recovery-009.md.invalid-pb-verified", "bridge/gtkb-wi5144-hp08-current-head-finalization-recovery-009.md", "groundtruth.db"]
- allowed: `true`
- evaluator: `project-authorization-operation-time-enforcement` v`1`
- evaluator_sha256: `2FEEEAB2C1996740C9CED1CF42BB1FA215D13ED39BD4104118EF31D7D957995D`
- taxonomy: v`1` `7E7D8594EA624F07D9188D66E5FB93DF6E62472BBC202E2CD1DDEF53EEF23233`

| Operation | Allowed | Reason Code | Reason |
| --- | --- | --- | --- |
| `implementation_packet_create` | `true` | `allowed` | The requested operation and every target class are PAUTH-allowed. |
| `implementation_start` | `true` | `allowed` | The requested operation and every target class are PAUTH-allowed. |

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5907-wi5144-invalid-terminal-chain-repair`
- Operative file: `bridge\gtkb-wi5907-wi5144-invalid-terminal-chain-repair-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
