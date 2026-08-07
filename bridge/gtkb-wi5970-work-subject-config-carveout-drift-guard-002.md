GO
::init gtkb lo
::open test
author_identity: loyal-opposition/goose/G
author_harness_id: G
author_session_context_id: G-2026-08-06T20-01-18Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive;role=loyal-opposition;::init gtkb lo;build activity
author_metadata_source: session envelope (worker_role_provenance)

bridge_kind: lo_verdict
Document: gtkb-wi5970-work-subject-config-carveout-drift-guard
Version: 002
Author: Loyal Opposition (goose, harness G)
Date: 2026-08-07 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5970-work-subject-config-carveout-drift-guard-001.md

# Loyal Opposition Review — WI-5970 config/ carve-out completion + drift guard (NEW 001)

## Verdict

GO on bridge/gtkb-wi5970-work-subject-config-carveout-drift-guard-001.md. The
proposal completes the WI-5100 config/ platform carve-out (C1) and replaces the
enumeration-only regression test with a live-tree drift guard (C2), addressing a
verified defect where enumeration-based tests cannot fail for unlisted paths.
Owner Decisions / Input present (owner directive "File the carve-out fix");
spec-derived test plan including the live unblock proof and preimage-cleanliness
precondition. Code anchors verified. Both mandatory preflights pass.

## First-Line Role Eligibility And Review Independence

- Role: loyal-opposition (`::init gtkb lo`; session envelope worker_role_provenance).
- Reviewed artifact author_session_context_id `345fab55-33fc-40c1-933b-d2413de27158` differs from reviewer `G-2026-08-06T20-01-18Z`.
- No active draft claim held before publication.

## Applicability Preflight

- packet_hash: `sha256:3a8a6ef1a1848dc4b009c985a411dc3a1a8998b36b22117806b141e867ca0ce3`
- bridge_document_name: `gtkb-wi5970-work-subject-config-carveout-drift-guard`
- declared_target_paths: ["platform_tests/hooks/test_workstream_focus.py", "scripts/workstream_focus.py"]
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5970-work-subject-config-carveout-drift-guard-001.md`
- operative_file: `bridge/gtkb-wi5970-work-subject-config-carveout-drift-guard-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- warnings.author_metadata_warnings: []
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]
- blocking_errors: []

### Project Authorization Operation-Time Evaluation

- phase: `proposal`
- status: `allowed`
- reason_code: `allowed`
- authorization_id: `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730`
- authorization_version: `2`
- project_id: `PROJECT-GTKB-HOUSEKEEPING-HARDENING`
- authorization_source: `bridge/gtkb-wi5970-work-subject-config-carveout-drift-guard-001.md`
- requested_operations: ["implementation_packet_create", "implementation_start"]
- cohort: ["platform_tests/hooks/test_workstream_focus.py", "scripts/workstream_focus.py"]
- allowed: `true`
- evaluator: `project-authorization-operation-time-enforcement` v`1`
- evaluator_sha256: `2FEEEAB2C1996740C9CED1CF42BB1FA215D13ED39BD4104118EF31D7D957995D`
- taxonomy: v`1` `30729C621B931EFD3D495FC764195AE2D76470ED29EA4B0A55D3FB71601500B3`

| Operation | Allowed | Reason Code | Reason |
| --- | --- | --- | --- |
| `implementation_packet_create` | `true` | `allowed` | The requested operation and every target class are PAUTH-allowed. |
| `implementation_start` | `true` | `allowed` | The requested operation and every target class are PAUTH-allowed. |

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:blocked |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5970-work-subject-config-carveout-drift-guard`
- Operative file: `bridge\gtkb-wi5970-work-subject-config-carveout-drift-guard-001.md`
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

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Prior Deliberations

- Owner directive 2026-08-07 ("File the carve-out fix").
- `DELIB-202666054` — WI-5100 verification NO-GO (preimage-cleanliness + carve-out design).
- `WI-5100` (2026-07-09) — the original enumeration-based carve-out this completes.

## Positive Confirmations

1. Code anchor verified: `CURRENT_REPO_BRIDGE_OR_GOVERNANCE_PREFIXES`
   (workstream_focus.py:252-276) enumerates six config/ subdirs against the
   blanket `config/` APPLICATION_PREFIXES entry (line 241) — the enumeration
   defect is real.
2. C2 drift guard addresses the "test that lists paths cannot fail for unlisted
   paths" gap; the negative test case verifies the guard actually fails.
3. Blanket fallback preserved (`config/app-settings.toml` still
   application_product); no collateral classification change.
4. Preimage-cleanliness precondition (DELIB-202666054) enforced before start.
5. Owner Decisions present; spec-derived test plan; PAUTH allowed.
6. Preflights pass: preflight_passed true, missing_required_specs [], clause
   blocking gaps 0.

## Residual Risks (non-blocking)

- Over-broad carve-out widens governance classification; mitigated by the
  4-category no-collateral-change test and blanket-fallback retention.

## Spec-to-Test Mapping

| Spec / requirement | Proposed verification | Adequacy |
| --- | --- | --- |
| C1 platform config → governance | rewritten `test_classify_root_config_platform_carveout` | adequate |
| C2 drift guard | synthetic unknown subdir negative case | adequate |
| No collateral change | `test_classify_root_4_categories` | adequate |
| Live unblock | classify_root probe on two blocked targets | adequate |

## Commands Executed

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5970-work-subject-config-carveout-drift-guard`
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5970-work-subject-config-carveout-drift-guard`
3. Live read of APPLICATION_PREFIXES / CURRENT_REPO_BRIDGE_OR_GOVERNANCE_PREFIXES anchors

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
