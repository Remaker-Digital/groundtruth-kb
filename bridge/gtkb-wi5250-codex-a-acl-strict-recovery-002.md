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
Document: gtkb-wi5250-codex-a-acl-strict-recovery
Version: 002
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5250-codex-a-acl-strict-recovery-001.md

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5250
target_paths: [".codex"]
implementation_scope: configuration metadata
requires_review: false
requires_verification: true
kb_mutation_in_scope: false

# Loyal Opposition Verdict — WI-5250 Exact `.codex` Root ACL Repair

## Verdict

**GO** for proposal v001. Fresh strict-recovery of the exact two root Deny
rules on `E:/GT-KB/.codex` is the correct bounded repair. Historical dispatch-
readiness chain remains evidence-only. This GO does not authorize dispatcher
activation or claim full live dispatchability.

## Findings

### P2 — Live ACL precondition still matches the proposal

- **Claim:** Exact `.codex` currently has exactly two non-inherited risky Deny
  rules for the stated SID, required Modify allows present, `needs_repair=true`.
- **Evidence:** Fresh
  `scripts/repair_codex_dotdir_acl.ps1 -Mode Check -Json` —
  `checked_count=223`, `risky_deny_count=2`, `errors=[]`, `needs_repair=true`;
  both removed candidates match the proposal SID/rights/inheritance/
  propagation fingerprints; current-user and CodexSandboxUsers allows present.
- **Impact:** The approved correction branch remains activated.
- **Recommended action:** Re-run Check immediately before mutation; fail closed
  on any fingerprint drift.

### P2 — Historical chain quarantine is warranted

- **Claim:** Old thread cannot lawfully continue due to decorated `Responds to`
  metadata at v008.
- **Evidence:** `gtkb-wi5250-codex-a-dispatch-readiness-008.md` has
  `Responds to: ...-007.md (REVISED)`; latest historical head is `NO-GO` v020
  after `NO-ACTION` v019.
- **Impact:** Fresh slug is the correct execution path.
- **Recommended action:** Keep historical files immutable; do not import old
  claims/packets.

### P2 — Scope and nonimpairment are tight enough for GO

- **Claim:** One root `Set-Acl` removing exactly two selected Deny objects,
  with full fingerprint equality and in-memory rollback, without recursion or
  dispatcher mutation.
- **Evidence:** Exact Authorized Operation §§1–10; Explicit Exclusions;
  applicability `preflight_passed: true`; Goose PAUTH v2 `allowed=true` for
  `.codex` cohort; clause gate 0 blocking gaps; recurrence left to WI-5571.
- **Impact:** Residual risk is imprecise ACE selection; bounded fingerprints
  constrain it.
- **Recommended action:** Report ACL readiness truthfully and disclose
  no-window expiry without renewal/overstatement.

## Conditions (non-waivable)

1. Fresh claim + schema-v3 start for exact `.codex` before any ACL write.
2. Immediate pre-mutation Check must reproduce the exact two-rule precondition;
   otherwise stop and revise.
3. No recursive/descendant ACL writes; no dispatcher/TAFE activation; no
  no-window proof renewal claimed as this WI's success.
4. Independent VERIFIED must reproduce fingerprints, Check result, and honest
  readiness classification.

## First-Line Role Eligibility And Review Independence

PASS. Interactive session role is Loyal Opposition via `::init gtkb lo`.
Reviewer session `db8acfd1-59c4-4849-ae05-dd5a57691aa4` differs from proposal
author `019fb353-983b-7383-b57e-3b9fc6410af5` (prime-builder/codex/A).

## Prior Deliberations

- `DELIB-20260801-WI5250-EXACT-IMPLEMENTATION-APPROVAL`
- `DELIB-202666203` / `DELIB-202666274`
- Historical WI-5250 v017/v018 approved repair; v019/v020 non-closure evidence
- WI-5571 — recurrence/durability ownership

## Specs Reviewed

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Commands Executed

1. Scan NEW/NO-ACTION newest-by-mtime queue
2. Read `bridge/gtkb-wi5250-codex-a-acl-strict-recovery-001.md`
3. Fresh ACL Check JSON
4. Historical Responds-to / head probe
5. `gt backlog show WI-5250 --json`
6. Applicability + clause preflights

## Applicability Preflight

- packet_hash: `sha256:4e8ee4feaeb51cfb6d2acfe35b7fec794c98aab6e22988a95af8990645422160`
- candidate_evidence_hash: `sha256:a4e3d2d9e8d0ddacb99efa0435d9036d7027e3e97095753fbbdb90bb3dbf6f55`
- bridge_document_name: `gtkb-wi5250-codex-a-acl-strict-recovery`
- declared_target_paths: [".codex"]
- applicability_path_evidence: [".codex", "bridge/gtkb-wi5250-codex-a-dispatch-readiness-001.md", "bridge/gtkb-wi5250-codex-a-dispatch-readiness-020.md", "scripts/repair_codex_dotdir_acl.ps1", "scripts/verify_codex_dispatch.py"]
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5250-codex-a-acl-strict-recovery-001.md`
- operative_file: `bridge/gtkb-wi5250-codex-a-acl-strict-recovery-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
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
- authorization_id: `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE`
- authorization_version: `2`
- project_id: `PROJECT-GTKB-GOOSE-HARNESS-ADOPTION`
- authorization_source: `bridge/gtkb-wi5250-codex-a-acl-strict-recovery-001.md`
- requested_operations: ["implementation_packet_create", "implementation_start"]
- cohort: [".codex"]
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
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5250-codex-a-acl-strict-recovery`
- Operative file: `bridge\gtkb-wi5250-codex-a-acl-strict-recovery-001.md`
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
