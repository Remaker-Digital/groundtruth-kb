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
Document: gtkb-wi5911-codex-acl-exact-root-apply
Version: 002
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5911-codex-acl-exact-root-apply-001.md

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5911
Related Work Items: WI-5250, WI-5571
target_paths: ["scripts/repair_codex_dotdir_acl.ps1", "platform_tests/scripts/test_repair_codex_dotdir_acl.py", "platform_tests/scripts/test_codex_dotdir_acl_repair.py"]
implementation_scope: source and tests
requires_review: false
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# Loyal Opposition Verdict — WI-5911 Exact-Root Fingerprint-Preserving Codex ACL Apply

## Verdict

**GO** for proposal v001. Replacing broad Apply normalization
(`PurgeAccessRules` / inheritance enable / allow synthesis / descendant repair)
with exact root `RemoveAccessRuleSpecific`, full non-target fingerprint
equality, one root write, and bounded complete-descriptor rollback is the
correct helper correction delegated from WI-5250 post-operation reconciliation.
This GO does **not** authorize live `.codex` ACL mutation or dispatcher/TAFE
activation.

## Findings

### P1 — Helper Apply path still mismatches the exact algorithm (defect confirmed)

- **Claim:** Current Apply still uses broad identity/inheritance/descendant
  mutation primitives rather than exact root rule-object removal.
- **Evidence:** Fresh source probe of
  `scripts/repair_codex_dotdir_acl.ps1` — `PurgeAccessRules` present;
  `Enable-AccessInheritance` present; `inheritance:e` present;
  `AddAccessRule` present; `Get-ChildItem` present;
  `RemoveAccessRuleSpecific` absent. Matches proposal Defect Evidence and
  WI-5250 REVISED `-003` acceptance-halt rationale.
- **Impact:** Future ACL repairs can silently alter non-target ACEs,
  inheritance, allows, or descendants even when the intended Deny rules are
  removed.
- **Recommended action:** Implement the exact in-memory transformation + one
  root `Set-Acl` + immediate readback + bounded rollback design as proposed.

### P2 — Target baseline and live `.codex` post-state revalidate

- **Claim:** Declared three-path SHA cohort is current; live Check is clean
  and this WI does not need another live ACL mutation to prove the helper fix.
- **Evidence:** Fresh SHA-256 match for all three targets
  (`D104B292…ED38`, `670AB079…2B06`, `56C4AEE8…1747`). Live Check JSON —
  `checked_count=223`, `risky_deny_count=0`, `errors=[]`,
  `needs_repair=false`. Active membership on
  `PROJECT-GTKB-GOOSE-HARNESS-ADOPTION`.
- **Impact:** Implementation can proceed against clean targets without
  conflating helper correction with live ACL incident repair.
- **Recommended action:** Re-hash the three targets immediately before
  claim/start; fail closed on drift. Keep tests off the live `.codex` ACL.

### P2 — Scope, PAUTH, TEST-11829, and exclusions are coherent

- **Claim:** Three-path source/test cohort under Goose PAUTH v2 is allowed;
  Check remains read-only; live `.codex` / dispatcher / verifier are excluded.
- **Evidence:** Applicability `preflight_passed: true`; PAUTH
  `allowed=true` for packet/start; clause gate 0 blocking gaps; proposal
  Explicit Exclusions forbid live ACL mutation, descendant writes, and
  dispatcher/TAFE actions; `TEST-11829` linked as integration contract.
- **Impact:** Low design risk if implementation stays inside the three
  declared paths and fixture-only tests.
- **Recommended action:** Enforce static rejection of broad APIs; keep
  dispatch-readiness truth separate from helper correctness.

## Conditions (non-waivable)

1. Fresh exact `go_implementation` claim and schema-v3 start packet covering
   all three declared paths; current overlap clearance; target bytes match the
   proposal baseline or exact hunk attribution.
2. No live `.codex` ACL mutation in implementation or tests; Apply changes are
   proven on controlled fixtures.
3. No dispatcher/TAFE activation, proof renewal, credential/deploy/release,
   Git/index mutation, or edits outside the three declared targets.
4. Independent VERIFIED remains required before terminal acceptance.

## First-Line Role Eligibility And Review Independence

PASS. Interactive session role is Loyal Opposition via `::init gtkb lo`.
Reviewer session `db8acfd1-59c4-4849-ae05-dd5a57691aa4` differs from proposal
author `019fb19b-7814-73c1-8707-204e432cbf00` (prime-builder/codex/A).

## Prior Deliberations

- `bridge/gtkb-wi5250-codex-a-acl-strict-recovery-003.md` — REVISED
  acceptance halt; delegates helper correction to WI-5911 / TEST-11829.
- `DELIB-20260801-WI5250-EXACT-IMPLEMENTATION-APPROVAL` — exact bounded
  root-rule correction that exposed the helper mismatch.
- WI-5571 — ACL recurrence/durability (not duplicated here).

## Specs Reviewed

- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`

## Commands Executed

1. NEW/NO-ACTION newest-by-mtime queue scan (tick head: WI-5911)
2. Read proposal `-001.md`; SHA-256 verify three targets
3. Source needle probe for broad Apply APIs
4. Live `repair_codex_dotdir_acl.ps1 -Mode Check -Json`
5. Membership + WI-5250 recovery head probe; applicability + clause preflights

## Applicability Preflight

- packet_hash: `sha256:8fb511fd2489b70323e2d9a215e5312718ea17946c5b12987003e16c1a8ba56c`
- candidate_evidence_hash: `sha256:633d64f1521aa8ba6168754ccd438f0a8d0ea036eca3ab490a3b3d1623d3258e`
- bridge_document_name: `gtkb-wi5911-codex-acl-exact-root-apply`
- declared_target_paths: ["platform_tests/scripts/test_codex_dotdir_acl_repair.py", "platform_tests/scripts/test_repair_codex_dotdir_acl.py", "scripts/repair_codex_dotdir_acl.ps1"]
- applicability_path_evidence: ["bridge/`.", "bridge/gtkb-wi5250-codex-a-acl-strict-recovery-003.md`", "platform_tests/scripts/test_codex_dotdir_acl_repair.py", "platform_tests/scripts/test_codex_dotdir_acl_repair.py`", "platform_tests/scripts/test_repair_codex_dotdir_acl.py", "platform_tests/scripts/test_repair_codex_dotdir_acl.py`", "scripts/repair_codex_dotdir_acl.ps1", "scripts/repair_codex_dotdir_acl.ps1`", "scripts/verify_codex_dispatch.py", "scripts/verify_codex_dispatch.py`,"]
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5911-codex-acl-exact-root-apply-001.md`
- operative_file: `bridge/gtkb-wi5911-codex-acl-exact-root-apply-001.md`
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
- authorization_source: `bridge/gtkb-wi5911-codex-acl-exact-root-apply-001.md`
- requested_operations: ["implementation_packet_create", "implementation_start"]
- cohort: ["platform_tests/scripts/test_codex_dotdir_acl_repair.py", "platform_tests/scripts/test_repair_codex_dotdir_acl.py", "scripts/repair_codex_dotdir_acl.ps1"]
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

- Bridge id: `gtkb-wi5911-codex-acl-exact-root-apply`
- Operative file: `bridge\gtkb-wi5911-codex-acl-exact-root-apply-001.md`
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

## Mandatory Closing Checklist

- [x] Status token is `GO`
- [x] Responds to exact latest path `-001.md`
- [x] Session-context review independence preserved
- [x] No live `.codex` / dispatcher authorization
- [x] No protected-file mutations in this verdict

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
