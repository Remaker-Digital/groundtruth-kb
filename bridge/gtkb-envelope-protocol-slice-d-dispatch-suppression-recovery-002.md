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

# Envelope Protocol Slice D Recovery GO — Application-Subject Suppression Ordering

bridge_kind: lo_verdict
Document: gtkb-envelope-protocol-slice-d-dispatch-suppression-recovery
Version: 002
Author: Loyal Opposition (Cursor, harness E)
Date: 2026-08-02 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-envelope-protocol-slice-d-dispatch-suppression-recovery-001.md
Work Item: WI-5376
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL

---

## Verdict Summary

**GO** for the narrowly bounded recovery: move application-subject Prime
dispatch suppression before work-intent and target-path filtering, and add
negative tests that fail if those filters are reached under an `application`
subject. Targets only `scripts/dispatcher_runtime.py` and
`platform_tests/scripts/test_dispatcher_runtime.py`.

Defect reproduced at review time: in the Prime branch,
`_filter_prime_selected_by_work_intent` / `_filter_prime_selected_by_target_paths`
still execute before `_application_subject_dispatch_suppression`
(`dispatcher_runtime.py` ~7142/7165 before ~7226). Preflights pass; lifecycle
is strict. Historical Slice D chain remains quarantined evidence.

---

## Binding Start Holds (hard)

1. **WI-5629 / WI-5786 terminal gate.** Do not begin protected mutation until
   WI-5629 is genuinely terminal via WI-5786 strict recovery. Current head
   `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-010.md` is `NO-GO` and
   does **not** satisfy this proposal’s precondition 2.
2. **Projection lane.** Keep
   `bridge/gtkb-retire-ipa-refs-skill-projections-006.md` independently
   `VERIFIED` and `config/agent-control/harness-capability-registry.toml` clean
   at HEAD before start.
3. **Target lock.** Exact claim + schema-v3 start for only the two declared
   paths. Forbidden: `.api-harness/routing.toml`, `.claude/settings.json`,
   `config/dispatcher/rules.toml`, TAFE activation.
4. **Regression shape.** Tests must assert filters are unreachable under
   application subject (monkeypatch fail-if-called); do not rely on timeout
   races or contention-sensitive passes.
5. **Owner approval scope.** `DELIB-20260801-WI5376-GOVERNED-RECOVERY-PROPOSAL-APPROVAL`
   authorizes this proposal/review path only — not a claim/start bypass.

---

## Prior Deliberations

- `DELIB-20260801-WI5376-GOVERNED-RECOVERY-PROPOSAL-APPROVAL`
- Historical
  `gtkb-envelope-protocol-slice-d-worker-hook-injection` v024 NO-GO (ordering
  defect preserved)

---

## Applicability Preflight

- packet_hash: `sha256:b150a57b610d2127dfaaa3f8905b650c3dd816e6d4fdfb8e105072f695093483`
- candidate_evidence_hash: `sha256:4f3d2dd49306ff5be4c6ef7b945307f43694016f4f668f313df064d21970410d`
- bridge_document_name: `gtkb-envelope-protocol-slice-d-dispatch-suppression-recovery`
- declared_target_paths: ["platform_tests/scripts/test_dispatcher_runtime.py", "scripts/dispatcher_runtime.py"]
- applicability_path_evidence: [".claude/settings.json", "bridge/gtkb-envelope-protocol-slice-d-worker-hook-injection-022.md`", "bridge/gtkb-envelope-protocol-slice-d-worker-hook-injection-023.md`", "bridge/gtkb-envelope-protocol-slice-d-worker-hook-injection-024.md`", "bridge/gtkb-retire-ipa-refs-skill-projections-006.md`", "bridge/gtkb-wi5786-wi5629-false-terminal-recovery-010.md`", "config/agent-control/harness-capability-registry.toml`", "config/dispatcher/rules.toml`.", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime.py::test_application_subject_suppresses_prime_dispatch_before_acquire_or_spawn`,", "platform_tests/scripts/test_dispatcher_runtime.py::test_gtkb_subject_allows_cross_harness_dispatch_negative_control`", "platform_tests/scripts/test_dispatcher_runtime.py`", "scripts/dispatcher_runtime.py", "scripts/dispatcher_runtime.py`", "scripts/dispatcher_runtime.py`,"]
- content_source: `pending_content`
- content_file: `bridge/gtkb-envelope-protocol-slice-d-dispatch-suppression-recovery-001.md`
- operative_file: `bridge/gtkb-envelope-protocol-slice-d-dispatch-suppression-recovery-001.md`
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
- authorization_id: `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL-20260716-PROJECT-SCOPE`
- authorization_version: `1`
- project_id: `PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL`
- authorization_source: `bridge/gtkb-envelope-protocol-slice-d-dispatch-suppression-recovery-001.md`
- requested_operations: ["implementation_packet_create", "implementation_start"]
- cohort: ["platform_tests/scripts/test_dispatcher_runtime.py", "scripts/dispatcher_runtime.py"]
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
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-envelope-protocol-slice-d-dispatch-suppression-recovery`
- Operative file: `bridge\gtkb-envelope-protocol-slice-d-dispatch-suppression-recovery-001.md`
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
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-envelope-protocol-slice-d-dispatch-suppression-recovery
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-envelope-protocol-slice-d-dispatch-suppression-recovery
# dispatcher_runtime.py: filters ~7142/7165 before suppression ~7226
# WI-5786 head: NO-GO v010
```

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
