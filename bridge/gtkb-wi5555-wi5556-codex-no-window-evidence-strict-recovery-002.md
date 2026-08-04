GO
::init gtkb lo
::open test
author_identity: loyal-opposition/cursor/E
author_harness_id: E
author_session_context_id: 33ad40f0-18df-4414-8f55-a11ecc7ad070
author_model: Composer
author_model_version: composer
author_model_configuration: Cursor IDE interactive; resolved role loyal-opposition; ::open build; goal continuous NEW/NO-ACTION drain
author_metadata_source: current interactive session envelope 33ad40f0-18df-4414-8f55-a11ecc7ad070

# WI-5555/WI-5556 GO — Codex No-Window Evidence Strict Recovery

bridge_kind: lo_verdict
Document: gtkb-wi5555-wi5556-codex-no-window-evidence-strict-recovery
Version: 002
Author: Loyal Opposition (Cursor, harness E)
Date: 2026-08-02 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5555-wi5556-codex-no-window-evidence-strict-recovery-001.md
Work Item: WI-5555
Work Item: WI-5556
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION

---

## Verdict Summary

**GO** for the six-path strict recovery: exact return-code success typing
(exclude `bool`/`float` zeros) and fail-closed `codex_models_manager::` ERROR
classification on the shared schema-v3 validator path.

Fresh thread correctly replaces the historical strict-invalid chain. Preflights
pass; lifecycle is `strict`; all six declared SHA-256 values MATCH at review
time; worktree targets clean. Defect confirmed: membership in `{0, "0"}` at
`codex_no_window_verification.py:27` and `:70`.

---

## Binding Start Holds

1. **Exact cohort only** — the six declared paths; no dispatcher/TAFE/harness
   activation; no external model-cache/credential reads.
2. **Shared-target recheck** — `platform_tests/scripts/test_dispatcher_runtime.py`
   is also under Slice D recovery GO
   (`gtkb-envelope-protocol-slice-d-dispatch-suppression-recovery-002`). Before
   start, confirm no concurrent claim/start overlap; sequence or disposition
   shared hunks.
3. **Hash/currentness recheck** at claim/start; drift fails closed → revise.
4. **No commit under this PAUTH** — PAUTH forbids `git_commit`; finalization
   needs separate authority after VERIFIED.
5. **Do not implement from historical invalid-chain GO** — this thread only.

---

## Prior Deliberations

- `DELIB-202667749` — project reactivation.
- `DELIB-202666274` / `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION`
- Historical `gtkb-wi5555-wi5556-codex-no-window-evidence-strictness` (evidence
  only).

---

## Applicability Preflight

- packet_hash: `sha256:31c9067366cda0884d8d09086e15cb7d24dff54f459d2d2b3782c5db0e9d1fb8`
- candidate_evidence_hash: `sha256:ae62fc7447c5e23cea9cb65b80f6b24d9dba01611d54d2d231bcc178bd569435`
- bridge_document_name: `gtkb-wi5555-wi5556-codex-no-window-evidence-strict-recovery`
- declared_target_paths: ["groundtruth-kb/src/groundtruth_kb/codex_no_window_verification.py", "groundtruth-kb/tests/test_codex_no_window_verification.py", "platform_tests/scripts/test_codex_no_window_smoke_probe.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_verify_codex_dispatch.py", "scripts/codex_no_window_smoke_probe.py"]
- applicability_path_evidence: ["bridge/gtkb-wi5389-codex-no-window-schema-contract-004.md`", "groundtruth-kb/src/groundtruth_kb/codex_no_window_verification.py", "groundtruth-kb/src/groundtruth_kb/codex_no_window_verification.py`", "groundtruth-kb/tests/test_codex_no_window_verification.py", "groundtruth-kb/tests/test_codex_no_window_verification.py`", "platform_tests/scripts/test_codex_no_window_smoke_probe.py", "platform_tests/scripts/test_codex_no_window_smoke_probe.py`", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime.py`", "platform_tests/scripts/test_verify_codex_dispatch.py", "platform_tests/scripts/test_verify_codex_dispatch.py`", "scripts/codex_no_window_smoke_probe.py", "scripts/codex_no_window_smoke_probe.py`"]
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5555-wi5556-codex-no-window-evidence-strict-recovery-001.md`
- operative_file: `bridge/gtkb-wi5555-wi5556-codex-no-window-evidence-strict-recovery-001.md`
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
- authorization_source: `bridge/gtkb-wi5555-wi5556-codex-no-window-evidence-strict-recovery-001.md`
- requested_operations: ["implementation_packet_create", "implementation_start"]
- cohort: ["groundtruth-kb/src/groundtruth_kb/codex_no_window_verification.py", "groundtruth-kb/tests/test_codex_no_window_verification.py", "platform_tests/scripts/test_codex_no_window_smoke_probe.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_verify_codex_dispatch.py", "scripts/codex_no_window_smoke_probe.py"]
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
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5555-wi5556-codex-no-window-evidence-strict-recovery`
- Operative file: `bridge\gtkb-wi5555-wi5556-codex-no-window-evidence-strict-recovery-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0

| Clause | Spec | Applicability | Evidence found |
|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — |

---

## Commands Executed

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5555-wi5556-codex-no-window-evidence-strict-recovery
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5555-wi5556-codex-no-window-evidence-strict-recovery
# six SHA-256 MATCH; defect at {0,"0"} lines 27 and 70
```

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
